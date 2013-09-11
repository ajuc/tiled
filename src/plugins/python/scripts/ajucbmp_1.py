"""
AjucBmp support for Tiled
2013, <ajuc00 AT g/\/\ail (om>
"""
from tiled import *
from tiled.qt import *
import os, sys, struct
from threading import Thread
import threading

maps = []
#threading.stack_size(67108864*2)

def parseName(fn):
  parts = fn.split(".")
  return ".".join(parts[:-1]), parts[-1]

def rgbaFromInt(i, bitsPerChannel=8):
  # save bitsPerChannel bits of i to each channel
  # i can have maximum of 4*bitsPerChannel bits
  # (so there are a little more than 1 000 000 tile numbers possible)
  # bitsPerChannel must be between 1 and 8 inclusively
  if bitsPerChannel < 1 or bitsPerChannel >8:
    return None

  mask = (2**(bitsPerChannel))-1

  freeBits = 8-bitsPerChannel
  return [
    ((i & (mask<<(bitsPerChannel*3)))>>(bitsPerChannel*3))<<freeBits,
    ((i & (mask<<(bitsPerChannel*2)))>>(bitsPerChannel*2))<<freeBits,
    ((i & (mask<<(bitsPerChannel  )))>>(bitsPerChannel  ))<<freeBits,
    ((i & (mask)))<<freeBits
  ]

def rgbaFromFloat(i, bitsPerChannel=8):
  return rgbaFromInt(i*256.0, bitsPerChannel) #TODO better conversion

class AjucBmp1(Plugin):
  @classmethod
  def nameFilter(cls):
    print ("nameFilter")
    return "AjucBmp1 (*.bmp)"

  @classmethod
  def supportsFile(cls, f):
    print ("supportsFile")
    return True
    #open(f).read(4) == 'FORM'

  @classmethod
  def read(cls, f):
    print ("read")
    return False

  @classmethod
  def bmp_write(cls, d, databytes, filename):
    mn1 = struct.pack('<B',d['mn1'])
    mn2 = struct.pack('<B',d['mn2'])
    filesize = struct.pack('<L',d['filesize'])
    undef1 = struct.pack('<H',d['undef1'])
    undef2 = struct.pack('<H',d['undef2'])
    offset = struct.pack('<L',d['offset'])
    headerlength = struct.pack('<L',d['headerlength'])
    width = struct.pack('<L',d['width'])
    height = struct.pack('<L',d['height'])
    colorplanes = struct.pack('<H',d['colorplanes'])
    colordepth = struct.pack('<H',d['colordepth'])
    compression = struct.pack('<L',d['compression'])
    imagesize = struct.pack('<L',d['imagesize'])
    res_hor = struct.pack('<L',d['res_hor'])
    res_vert = struct.pack('<L',d['res_vert'])
    palette = struct.pack('<L',d['palette'])
    importantcolors = struct.pack('<L',d['importantcolors'])
    #create the outfile
    outfile = open(filename,'wb')
    #write the header + the bytes
    outfile.write(mn1+mn2+filesize+undef1+undef2+offset+headerlength+width+height+\
                  colorplanes+colordepth+compression+imagesize+res_hor+res_vert+\
                  palette+importantcolors+databytes)
    outfile.close()

  @classmethod
  def getHeader(cls, width, height):
    return {
        'mn1':66,
        'mn2':77,
        'filesize':0,
        'undef1':0,
        'undef2':0,
        'offset':54,
        'headerlength':40,
        'width': width, #200,
        'height': height, #200,
        'colorplanes':1,
        'colordepth':32,
        'compression':0,
        'imagesize':0,
        'res_hor':0,
        'res_vert':0,
        'palette':0,
        'importantcolors':0
    }


  @classmethod
  def writeDescriptor(cls, m, filesDir, fn):
    print ("writeDescriptor fn="+fn)

    outfile = open(filename,'w')
    try:
      outfile.write(str(filesDir)+"\n")
    catch:
      return False
    finally:
      outfile.close()
    return True

  @classmethod
  def writeTiles(cls, m, fn):
    print ("writeTiles fn="+fn+" not implemented yet")
    return True

  @classmethod
  def writeSprites(cls, m, fn):
    print ("writeSprites fn="+fn+" not implemented yet")
    return True

  @classmethod
  def writeMap(cls, m, i, fn):
    print ("writeMap i="+str(i)+" fn="+fn)
    padding=None
    databytes = bytes()
    l = tileLayerAt(m, i)
    w=l.width()
    h=l.height()
    pixels = [[0, 0, 0, 0] for sth in xrange(w*h)]
    for y in range(l.height()-1,-1,-1):# (BMPs are L to R from the bottom L row)
      for x in range(l.width()):
        if l.cellAt(x, y).tile != None:
          pixels[x+(h-1-y)*w]=rgbaFromInt(l.cellAt(x, y).tile.id())
        else:
          pixels[x+(h-1-y)*w]=rgbaFromInt(0)
    header_dict = cls.getHeader(w, h)
    for y in xrange(h):# (BMPs are L to R from the bottom L row)
      for x in xrange(w):
        pixel = struct.pack('<BBBB',
                            pixels[x+(y)*w][0],
                            pixels[x+(y)*w][1],
                            pixels[x+(y)*w][2],
                            pixels[x+(y)*w][3])
        databytes = databytes + pixel
      row_mod = (w*header_dict['colordepth']/8) % 4
      if row_mod == 0:
          padding = 0
      else:
          padding = (4 - row_mod)
      padbytes = bytes()
      for i in xrange(padding):
          column = struct.pack('<B',0)
          padbytes = padbytes + y
      databytes = databytes + padbytes
    print ("PO zrobieniu tablicy. len(databytes)=" + str(len(databytes)))
    cls.bmp_write(header_dict, databytes, fn)
    return True


  @classmethod
  def serializedObject(cls, obj):
    print ("serializedObject")
    x = [
      'cell',
      'height',
      'property',
      'shape',
      'width',
      'x',
      'y'
    ]
    print ("obj.x="+str(obj.x()))
    print ("obj.y="+str(obj.y()))
    print ("obj.width="+str(obj.width()))
    print ("obj.height="+str(obj.height()))
    print ("obj.shape="+str(obj.shape()))
    print ("dir(obj.property)="+str(dir(obj.property)))

    print ("obj.property(\"id\")="+str(obj.property("id")))
    print ("obj.property(\"spriteNo\")="+str(obj.property("spriteNo")))
    print ("obj.property(\"somethingElseAltogether\")="+str(obj.property("somethingElseAltogether")))

    print ("dir(obj.cell)="+str(dir(obj.cell())))
    print ("obj.name="+str(obj.name()))
    print ("obj.rotation="+str(obj.rotation()))
    print ("obj.isVisible="+str(obj.isVisible()))

    bitsPerChannel = 8

    outPixelsArray += [
      rgbaFromInt(obj.property("id"), bitsPerChannel),                #0
      rgbaFromInt(obj.property("parentId"), bitsPerChannel),          #1
      rgbaFromInt(obj.property("groupId"), bitsPerChannel),           #2

      rgbaFromInt(obj.property("spriteNo"), bitsPerChannel),          #3

      rgbaFromFloat(obj.property("mass"), bitsPerChannel),            #4
      rgbaFromFloat(obj.property("momentOfInertia"), bitsPerChannel), #5
      rgbaFromFloat(obj.property("friction"), bitsPerChannel),        #6

      rgbaFromFloat(obj.property("vx"), bitsPerChannel),              #7
      rgbaFromFloat(obj.property("vy"), bitsPerChannel),              #8
      rgbaFromFloat(obj.property("angularVelocity"), bitsPerChannel), #9

      rgbaFromFloat(obj.x(), bitsPerChannel),                         #10
      rgbaFromFloat(obj.y(), bitsPerChannel),                         #11
      rgbaFromFloat(obj.rotation(), bitsPerChannel),                  #12
      rgbaFromFloat(obj.width(), bitsPerChannel),                     #13
      rgbaFromFloat(obj.height(), bitsPerChannel)                     #14
    ]

    return True

  @classmethod
  def writeObjects(cls, m, i, fn):
    print ("writeObjects i="+str(i)+" fn="+fn)
    og = objectGroupAt(m, i)
    for x in range(og.objectCount()):
      cls.writeObject(og.objectAt(x), outPixelsArray)
    return True


  @classmethod
  def write(cls, m, fn):
    print ("write fn="+fn)
    name, extension = parseName(fn)
    allOk = True
    filesDir = {}
    for i in xrange(m.layerCount()):
      if isTileLayerAt(m, i):
        print ("layer("+str(i)+") is a tile layer")
        fnTmp = name+"_map_"+str(i)+"_"+extension
        filesDir[fnTmp] = i
        allOk = allOk and cls.writeMap(m, i, fnTmp)
      elif isObjectGroupAt(m, i):
        print ("layer("+str(i)+") is an object layer")
        fnTmp = name+"_obj_"+str(i)+"_"+extension
        filesDir[fnTmp] = i
        allOk = allOk and cls.writeObjects(m, i, fnTmp)

    fnTmp = name+"_tiles_"+extension
    filesDir[fnTmp] = 0
    allOk = allOk and cls.writeTiles(m, fnTmp)

    fnTmp = name+"_sprites_"+extension
    filesDir[fnTmp] = 0
    allOk = allOk and cls.writeSprites(m, fnTmp)

    allOk = allOk and cls.writeDescriptor(m, filesDir, fn+"_descriptor_")

    return allOk

