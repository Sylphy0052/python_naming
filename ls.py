import binascii
import numpy as np
# -*- coding: utf-8 -*-

class Filsys:
    def __init__(self, datas):
        pc = 0
        self.s_isize, pc = self.read_int16(datas, pc) # int16
        self.s_fsize, pc = self.read_int16(datas, pc)
        self.s_nfree, pc = self.read_int16(datas, pc)
        self.s_free, pc = self.read_loop_int16(datas, pc, 100)
        self.s_ninod, pc = self.read_int16(datas, pc)
        self.s_inode, pc = self.read_loop_int16(datas, pc, 100)
        self.s_flock, pc = self.read_int8(datas, pc)
        self.s_ilock, pc = self.read_int8(datas, pc)
        self.s_fmod, pc = self.read_int8(datas, pc)
        self.s_ronly, pc = self.read_int8(datas, pc)
        self.s_time, pc = self.read_loop_int16(datas, pc, 2)
        self.pad, pc = self.read_loop_int16(datas, pc, 48)

    def read_int8(self, datas, pc):
        ret = int.from_bytes(datas[pc : pc + INT8], ENDIAN)
        pc += INT8
        return ret, pc

    def read_int16(self, datas, pc):
        ret = int.from_bytes(datas[pc : pc + INT16], ENDIAN)
        pc += INT16
        return ret, pc

    def read_loop_int16(self, datas, pc, n):
        ret = [int.from_bytes(datas[i : i + INT16], ENDIAN) for i in range(pc, pc + INT16 * n - 1, BYTE)]
        pc += INT16 * n
        return ret, pc


class Inode:
    def __init__(self, datas):
        pc = 0
        self.i_mode, pc = self.read_int16(datas, pc)
        self.i_nlink, pc = self.read_int8(datas, pc)
        self.i_uid, pc = self.read_int8(datas, pc)
        self.i_gid, pc = self.read_int8(datas, pc)
        self.i_size0, pc = self.read_int8(datas, pc)
        self.i_size1, pc = self.read_int16(datas, pc)
        self.i_addr, pc = self.read_loop_int16(datas, pc, 8)
        self.i_astime, pc = self.read_loop_int16(datas, pc, 2)
        self.i_mtime, pc = self.read_loop_int16(datas, pc, 2)

    def read_int8(self, datas, pc):
        ret = int.from_bytes(datas[pc : pc + INT8], ENDIAN)
        pc += INT8
        return ret, pc

    def read_int16(self, datas, pc):
        ret = int.from_bytes(datas[pc : pc + INT16], ENDIAN)
        pc += INT16
        return ret, pc

    def read_loop_int16(self, datas, pc, n):
        ret = [int.from_bytes(datas[i : i + INT16], ENDIAN) for i in range(pc, pc + INT16 * n - 1, BYTE)]
        pc += INT16 * n
        return ret, pc

IALLC = 0o100000
IFMT = 0o60000
IFDIR = 0o40000
IFCHR = 0o20000
IFBLK = 0o60000
ILARG = 0o10000
ISUID = 0o4000
ISGID = 0o2000
ISVTX = 0o1000
IREAD = 0o400
IWRITE = 0o200
IEXEC = 0o100

BYTE = 2
INT8 = 1
INT16 = 2
BLOCK_SIZE = 512
INODE_SIZE = 32
ROOT_INODE = 0

ENDIAN = 'little'

def main():
    pc = 0
    datas = open("v6root", "rb").read()
    data_length = len(datas)
    # print("byte_length : ", data_length)

    # 読み飛ばし
    # print("This block is used when system is started running")
    # print(binascii.hexlify(datas[pc : pc + BLOCK_SIZE]))
    pc += BLOCK_SIZE

    # スーパーブロック
    # print("This block is super block")
    # print(binascii.hexlify(datas[pc : pc + BLOCK_SIZE]))
    filsys = Filsys(datas[pc : pc + BLOCK_SIZE])
    pc += BLOCK_SIZE
    # print("filsys")

    # inodes = Inode
    inode_num = filsys.s_isize
    # print("inode_num : ", filsys.s_isize)
    # print("inode 1")

    print("inode")
    inodes = []
    print(binascii.hexlify(datas[pc : pc + inode_num * INODE_SIZE]))
    for i in range(inode_num):
        num = i + 1
        inode = Inode(datas[pc : pc + INODE_SIZE])
        inodes.append(inode)
        print(i, "imode : ", oct(inode.i_mode))
        pc += INODE_SIZE

    strage_num = filsys.s_fsize
    print("strage_num : ", filsys.s_fsize)

    print("strage")
    strages = []
    print(binascii.hexlify(datas[pc : pc + strage_num * BLOCK_SIZE]))
    for i in range(strage_num):
        num = i + 1
        strage = datas[pc : pc + BLOCK_SIZE]
        strages.append(strage)
        pc += BLOCK_SIZE

    print("strage : ", hex(strages[0]))



    # inode = Inode(datas[pc : pc + NEXT])
    # inodes.append(inode)
    # pc += INODE_SIZE * BYTE
    # inode_number += 1

    # while(pc < data_length):
    #     print("inode 1")
    #     print(binascii.hexlify(datas[pc : pc + INODE_SIZE]))
    #
    #     inode = Inode(datas[pc : pc + NEXT])
    #     inodes.append(inode)
    #     pc += INODE_SIZE * BYTE
    #     inode_number += 1

if __name__ == '__main__':
    main()
