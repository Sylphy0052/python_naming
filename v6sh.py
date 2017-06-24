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

    def print_info(self):
        print('s_isize : {0}'.format(self.s_isize))
        print('s_fsize : {0}'.format(self.s_fsize))
        print('s_nfree : {0}'.format(self.s_nfree))
        print('s_free : {0}'.format(self.s_free))
        print('s_ninod : {0}'.format(self.s_ninod))
        print('s_inode : {0}'.format(self.s_inode))
        print('s_flock : {0}'.format(self.s_flock))
        print('s_ilock : {0}'.format(self.s_ilock))
        print('s_fmod : {0}'.format(self.s_fmod))
        print('s_ronly : {0}'.format(self.s_ronly))
        print('s_time : {0}'.format(self.s_time))
        print('pad : {0}'.format(self.pad))


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

    def print_info(self):
        print('i_mode : {0}'.format(oct(self.i_mode)))
        print('i_nlink : {0}'.format(self.i_nlink))
        print('i_uid : {0}'.format(self.i_uid))
        print('i_gid : {0}'.format(self.i_gid))
        print('i_size0 : {0}'.format(self.i_size0))
        print('i_size1 : {0}'.format(self.i_size1))
        print('i_addr : {0}'.format(self.i_addr))
        print('i_astime : {0}'.format(self.i_astime))
        print('i_mtime : {0}'.format(self.i_mtime))

class Dir:
    def __init__(self, ino, name):
        self.ino = ino
        self.name = name

    def print_info(self):
        self.ino.print_info()
        print('name : {0}'.format(self.name))

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
working_directory = []

def print_help():
    commands = ['ls [-l]',
                'cd dir_name',
                'inode inode_num',
                'filsys',
                'dir',
                'pwd',
                'help',
                'quit']

    descriptions = ['Display a list of files and directories',
                   'Change directory to dir_name',
                   'Display information of inode[inode_num]',
                   'Display information of filsys',
                   'Display information of current files or directories',
                   'Display the current directory name',
                   'Display help',
                   'Finish the program',
                   ]

    for i in range(len(commands)):
        print('{0:<17} : {1}'.format(commands[i], descriptions[i]))

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
            # 何もないの飛ばす
            if int.from_bytes(strage[pc + 2 : pc + NAME_SIZE], ENDIAN) == 0:
                pc += NAME_SIZE + 2
                continue

            dir_inode = inodes[int.from_bytes(strage[pc : pc + 2], ENDIAN) - 1]
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
        for dir_c in dir_list:
            option = ''
            inode = dir_c.ino
            file_size = math.ceil((inode.i_size0 << 8) + inode.i_size1)
            option += 'd' if inode.i_mode & IFDIR else '-'
            for i in range(3):
                imode = inode.i_mode << (i * 3)
                option += 'r' if imode & IREAD else '-'
                option += 'w' if imode & IWRITE else '-'
                option += 'x' if imode & IEXEC else '-'

            print("{0:>10} {1:>8} {2}".format(option, file_size, str(dir_c.name)))

    else:
        for dir_c in dir_list:
            print(str(dir_c.name))

def _cd(dir_name):
    global current_inode, inodes, working_directory
    dir_list = getDirList()
    if dir_name == '/':
        current_inode = inodes[ROOT_INODE]
        working_directory = ['/']
        return

    if dir_name == '..':
        working_directory.pop()
        if len(working_directory) == 0:
            working_directory = ['/']
    elif dir_name == '.':
        pass
    else:
        working_directory.append(dir_name)

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

def cd(dir_name):
    dir_names = dir_name.split('/')
    if dir_name[0] == '/':
        _cd(dir_name[0])

    for i in range(len(dir_names)):
        if dir_names[i] == '':
            continue
        else:
            _cd(dir_names[i])

def pwd():
    global working_directory
    print('/', end = '')
    if len(working_directory) == 1:
        pass
    else:
        for i in range(1, len(working_directory)):
            print(working_directory[i], end = '')
            if i != len(working_directory) - 1:
                print('/', end = '')
    # for dir_name in working_directory:
        # if dir_name[i] == '/':
        #     pass
        # else:
        #     print('/' + dir_name, end = '')
    print()

def main():
    global filsys, inodes, strages, current_inode, working_directory
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
    working_directory = ['/']

    while(True):
        print(">>", end=" ")
        command = input()
        commands = command.split(' ')
        command_len = len(commands)
        if commands[0] == "ls" and (command_len == 1 or (command_len == 2 and commands[1] == '')):
            ls(False)

        elif commands[0] == "ls" and (command_len == 2 and commands[1] == '-l'):
            ls(True)

        elif commands[0] == "cd" and command_len == 2:
            cd(commands[1])

        elif commands[0] == 'inode' and command_len == 2:
            inodes[int(commands[1])].print_info()

        elif commands[0] == 'filsys' and command_len == 1:
            filsys.print_info()

        elif commands[0] == 'dir' and command_len == 1:
            for dir_c in getDirList():
                dir_c.print_info()

        elif command == "pwd" and command_len == 1:
            pwd()

        elif command == "quit":
            break

        elif command == 'help':
            print_help()

        else:
            print('Undefined command...')
            print('Use \"help\"')

if __name__ == '__main__':
    main()
