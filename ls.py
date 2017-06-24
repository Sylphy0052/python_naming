import math
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

class Dir:
    def __init__(self, ino, name):
        self.ino = ino
        self.name = name

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
NAME_SIZE = 14

ENDIAN = 'little'

filsys = None
inodes = []
strages = []
current_inode = None

def getDirList():
    global filsys, inodes, strages, current_inode
    inode = current_inode
    dir_list = []
    for addr in inode.i_addr:
        if addr == 0:
            break
        offset = addr - filsys.s_isize - 2
        strage = strages[offset]
        pc = 0
        while(pc < BLOCK_SIZE):
            if int.from_bytes(strage[pc + 2 : pc + NAME_SIZE], ENDIAN) == 0:
                pc += NAME_SIZE + 2
                continue
            dir_inode = inodes[int.from_bytes(strage[pc : pc + 1], ENDIAN)]
            name = ''
            for c in strage[pc + 2 : pc + NAME_SIZE + 2].decode('utf-8'):
                if c == '\0':
                    break
                name += c

            dir_c = Dir(dir_inode, name)
            dir_list.append(dir_c)
            pc += NAME_SIZE + 2

    dir_list = sorted(dir_list, key=lambda dir_c: dir_c.name)
    return dir_list

def ls(flg):
    global filsys, inodes, strages, current_inode
    dir_list = getDirList()

    if flg:
        print("ls -l")
        for dir_c in dir_list:
            option = ''
            inode = dir_c.ino
            file_size = math.ceil((inode.i_size0 << 8) + inode.i_size1)
            option += 'r' if inode.i_mode & IFDIR else '-'
            for i in range(3):
                imode = inode.i_mode << (i * 3)
                option += 'r' if imode & IREAD else '-'
                option += 'w' if imode & IWRITE else '-'
                option += 'x' if imode & IEXEC else '-'

            print("{0:>10} {1:>8} {2}".format(option, file_size, str(dir_c.name)))

    else:
        for dir_c in dir_list:
            print(str(dir_c.name))

def cd(dir_name):
    global current_inode, inodes
    dir_list = getDirList()
    if dir_name == '/':
        current_inode = inodes[ROOT_INODE]
        return

    to_dir = None
    for dir_c in dir_list:
        if dir_c.name == dir_name:
            to_dir = dir_c
            break

    if to_dir == None:
        print("Not Found")
        return

    if to_dir.ino.i_mode & IFDIR:
        current_inode = to_dir.ino
    else:
        print("Not Directory")

def main():
    global filsys, inodes, strages, current_inode
    pc = 0
    datas = open("v6root", "rb").read()
    data_length = len(datas)

    # 読み飛ばし
    pc += BLOCK_SIZE

    # スーパーブロック
    filsys = Filsys(datas[pc : pc + BLOCK_SIZE])
    pc += BLOCK_SIZE

    inode_num = math.ceil(filsys.s_isize * BLOCK_SIZE / INODE_SIZE)

    for i in range(inode_num):
        inode = Inode(datas[pc : pc + INODE_SIZE])
        inodes.append(inode)
        pc += INODE_SIZE

    strage_num = filsys.s_fsize

    for i in range(strage_num):
        strage = datas[pc : pc + BLOCK_SIZE]
        strages.append(strage)
        pc += BLOCK_SIZE

    current_inode = inodes[ROOT_INODE]

    while(True):
        print(">>", end=" ")
        command = input()
        commands = command.split(' ')
        command_len = len(commands)
        print(commands)
        if commands[0] == "ls":
            if command_len == 1 or (command_len == 2 and commands[1] == ''):
                ls(False)
            elif command_len == 2 and commands[1] == '-l':
                ls(True)
        if commands[0] == "cd":
            if command_len != 2:
                print("cd dirname")
            else:
                cd(commands[1])

        elif command == "quit":
            break

if __name__ == '__main__':
    main()
