#!/usr/bin/python3

#MIT License

#Copyright (c) 2019 Jhoevine Capicio

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import os
import struct
import datetime
import sys
import time
import argparse

class deleted_file():
    def __init__(self):
        self.date = None
        self.size = None
        self.type = ''
        self.Ifile = ''
        self.Rfile = ''
        self.filepath = ''
        self.filename = ''
        self.file_dir = ''

def to_seconds(date):
    # https://stackoverflow.com/questions/6256703/convert-64bit-timestamp-to-a-readable-value
    s = float(date) / 1e7  # convert to seconds
    seconds = s - 11644473600  # number of seconds from 1601 to 1970
    # 'Sat Jan 26 03:27:21 2019'
    return datetime.datetime.strptime(time.ctime(seconds), '%a %b %d %H:%M:%S %Y')


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("rbindir",type=str,help="Directory containing the recyclebin contents or path of an I$ file.")
    parser.add_argument("--full", help="Get all contents including files in deleted directories", action="store_true")
    args = parser.parse_args()
    full_display = 0
    if args.full:
        full_display = 1

    deleted_files = []
    RecycleBin = args.rbindir.strip()

    # del_file = None
    if os.path.isdir(RecycleBin.strip()):
        for root, dirs, files in os.walk(RecycleBin):
        # for root, dirs, files in os.walk("D:\\Training Modules"):
            for file in files:
                if file[0:2] == '$I':
                    with open(os.path.join(root, file), "rb") as f:
                        del_file = deleted_file()
                        del_file.Ifile = file
                        del_file.Rfile = file.replace('$I', '$R')
                        header = f.read(8)
                        size = f.read(8)
                        del_file.size = int.from_bytes(size, byteorder='little')
                        date = f.read(8)
                        if header == b'\x02\x00\x00\x00\x00\x00\x00\x00':
                            filename_length = f.read(4)
                        del_file.filepath = str(f.read(), 'utf-8').replace('\x00', '').encode('ascii', 'ignore').decode(
                            'utf-8')
                        del_file.date = to_seconds(struct.unpack("<Q", date)[0])
                        del_file.filename = del_file.filepath.split('\\')[-1:][0]
                        if os.path.isdir(os.path.join(root,del_file.Rfile)):
                            del_file.type = "dir"
                        elif os.path.isfile(os.path.join(root,del_file.Rfile)):
                            del_file.type = "file"
                        deleted_files.append(del_file)
    elif os.path.isfile(RecycleBin.strip()):
        if os.path.basename(RecycleBin)[0:2] == '$I':
            with open(RecycleBin, "rb") as f:
                del_file = deleted_file()
                del_file.Ifile = RecycleBin.strip()
                del_file.Rfile = RecycleBin.replace('$I', '$R').strip()
                header = f.read(8)
                size = f.read(8)
                del_file.size = int.from_bytes(size, byteorder='little')
                date = f.read(8)
                if header == b'\x02\x00\x00\x00\x00\x00\x00\x00':
                    filename_length = f.read(4)
                del_file.filepath = str(f.read(), 'utf-8').replace('\x00', '').encode('ascii', 'ignore').decode(
                    'utf-8')
                del_file.date = to_seconds(struct.unpack("<Q", date)[0])
                del_file.filename = del_file.filepath.split('\\')[-1:][0]
                if os.path.isdir(del_file.Rfile):
                    del_file.type = "dir"
                elif os.path.isfile(del_file.Rfile):
                    del_file.type = "file"
                    print(del_file.Ifile)
                deleted_files.append(del_file)

    print('Date,Type,Size,Filepath,Filename,Ifile,Rfile')

    for del_file in deleted_files:
        if del_file.type == "dir":
            print ('%s,%s,%s,%s,%s,%s,%s' % (
            del_file.date, del_file.type,del_file.size, del_file.filepath.strip(), del_file.filename.strip(), os.path.basename(del_file.Ifile),
            os.path.basename(del_file.Rfile)))
            if full_display:
                for root,dir,files in os.walk(os.path.join(RecycleBin,del_file.Rfile)):
                    for file in files:
                        print('%s,%s,%s,%s,%s,%s,%s' % (
                            del_file.date, "dir content", os.path.getsize(os.path.join(RecycleBin,del_file.Rfile)), os.path.join(del_file.filepath,file).replace("/","\\"), file,"",""))
        #elif del_file.type == "file":
        else:
            print('%s,%s,%s,%s,%s,%s,%s' % (
                del_file.date, del_file.type, del_file.size, del_file.filepath.strip(), del_file.filename.strip(),
                os.path.basename(del_file.Ifile),
                os.path.basename(del_file.Rfile)))


if __name__ == '__main__':
    main()
