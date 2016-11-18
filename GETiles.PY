#!/usr/bin/env python
# encoding: utf-8

import os, sys, requests, struct

# urls:
# kh.google.com/dbRoot.v5 < 秘钥和地图版本信息
# kh.google.com/flatfile?q2-0-q.705 < QTree数据
# kh.google.com/flatfile?f1-030-i.704 < 瓦片图像
# 1. 

def Eval(fname, key):
    # 解码数据
    if (os.path.exists(fname)==False): return None
    if (os.path.getsize(fname)==0): return None
    f = open(fname, 'rb+')
    data = f.read()                             # 读取文件内容
    f.close()
    #outdata = [0 for i in range(len(data))]    # 创建一个结果数组
    outdata = bytearray(len(data))              # 创建一个结果数组
    
    index = 16
    for i in range(0, len(data)):
        outdata[i] = ord(data[i]) ^ ord(key[index+8])
        index += 1
        if (index % 8 == 0): index += 16
        if (index >= 1016): index = (index + 8) % 24
    return outdata

def ReadKEY(fname):
    # 读取KEY文件
    f = open(fname, 'rb+')
    data = f.read()
    f.close()
    return data

def ReadVersion(fname):
    # 读取dbRoot.v5文件里的版本号
    if (os.path.exists(fname)==False): return None
    if (os.path.getsize(fname)==0): return None
    f = open(fname, 'rb+')
    f.seek(6)
    value = f.read(2)
    f.close()
    version = struct.unpack('h', value)[0]
    version = version ^ 0x4200
    return version

def ReadDBRoot():
    # 读取dbRoot.v5文件
    # 详细说明 http://greverse.bitbucket.org/dbroot.htm
    # 00-03: 固定 9464874E
    # 04-05: 数据版本 6600
    # 06-07: 地图版本 比如 C240 需要与 0x4200 进行异或运算得出最终版本
    # 08-1023: 数据秘钥共1016字节
    # 1024-: 加密的XML数据
    pass

def Tile2QuadKEY(tileX, tileY, zoom):
    # 瓦片坐标转四叉树
    result = '0'
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if ((tileX & mask) != 0): digit += 1
        if ((tileY & mask) != 0): digit += 2
        # 由于谷歌四叉树算法和必应四叉树算法不一致
        # 所以取巧采用对照表的方法可以解决 但第一位始终是0
        # 对照表
        # 必应 -> 谷歌
        # 0 -> 3
        # 1 -> 2
        # 2 -> 0
        # 3 -> 1
        if (digit == 0): result += '3'
        elif (digit == 1): result += '2'
        elif (digit == 2): result += '0'
        elif (digit == 3): result += '1'
    return result

def QuadKEY2Tile(nums):
    # 四叉树转 反转的时候也必须通过对照表
    tileX = 0
    tileY = 0
    nums = nums[1:]       # 第一位是0所以取掉
    zoom = len(nums)
    
    for i in range(zoom, 0, -1):
        mask = 1 << (i - 1)
        if (nums[zoom - i] == '3'):
            continue
        elif (nums[zoom - i] == '2'):
            tileX |= mask
            continue
        elif (nums[zoom - i] == '0'):
            tileY |= mask
            continue
        elif (nums[zoom - i] == '1'):
            tileX |= mask
            tileY |= mask
            continue
    return tileX, tileY, zoom

def Hex2Time(data):
    # 十六进制转时间
    # data: 传入16进制数据
    month = int(data & 0xF)         # 月
    day = int((data & 0x1F0)>>4)    # 日
    year = int((data & 0xFFE00)>>9) # 年
    return year, month, day

def Time2Hex(year, month, day):
    # 时间转十六进制
    pass


if __name__ == '__main__':
    print '[==DoDo==]'
    print 'GE Tiles.'
    print 'Encode: %s' %  sys.getdefaultencoding()

    
    # 解密瓦片数据
    #keydata = ReadKEY('data/key.bin')
    #imgdata = Eval('data/flatfile-f1-021031102113-i.704', keydata)
    #f = open('out.jpg', 'wb')
    #f.write(imgdata)
    #f.flush()
    #f.close

    # 时间字符串转时间
    #Hex2Time(int('0xfa99b', 16))

    # 瓦片坐标和四叉树互转
    #print Tile2QuadKEY(3, 5, 3)
    #print 'X:%s Y:%s Z:%s' % QuadKEY2Tile('0021')

    # 读取地图版本
    #print ReadVersion('data/dbRoot.v5')

    # 解码QTree数据
    keydata = ReadKEY('data/key.bin')
    zlibdata = Eval('data/flatfile-q2-02103110-q.705', keydata)
    f = open('out.gz', 'wb')
    f.write(zlibdata)
    f.flush()
    f.close

    print 'OK.'
