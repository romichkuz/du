import os
import argparse
from enum import Enum
from pwd import getpwuid
import math
import time

class Type(Enum):
    DIR = 1,
    FILE = 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Путь до директории')
    parser.add_argument('--g', choices=['e', 'u'])

    return parser.parse_args()


def get_dir_size(path):
    total_size = 0
    for obj in os.scandir(path):
        try:
            if obj.is_symlink():
                continue
            if obj.is_file():
                total_size += obj.stat().st_size
            elif obj.is_dir():
                total_size += get_dir_size(obj.path)
        except PermissionError:
            pass
        
    return total_size


def get_size_MB(size):
    return size / 1024 / 1024


def get_progress_bar(count):
    return 'Progress [' + (count * '*') + (10 - count) * ' ' + ']'


def get_objs_sizes(path):
    objs = []
    objs_count = len(list(os.walk(path)))
    counter = 0
    
    for dirpath, dirnames, filenames in os.walk(path): 
        print("\033c", end="")
        counter += 1
        print(get_progress_bar(math.trunc(counter / objs_count * 10)))
        #time.sleep(0.01)

        dir_obj = {
            'path': dirpath,
            'size': get_dir_size(dirpath),
            'type': Type.DIR
        }
        objs.append(dir_obj)
        
        for filename in filenames:
            try:
                file_path = f'{dirpath}/{filename}'
                file = {
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'type': Type.FILE
                }

                objs.append(file)
            except FileNotFoundError:
                pass

    return objs



# GROUPING FUNCTIONALITY
def group_by(objs, group_func):
    res = {}
    for obj in objs:
        key = group_func(obj)

        if key not in res:
            res[key] = []
        res[key].append(obj)
    
    return res
            

def group_by_ext(obj):
    if obj['type'] == Type.DIR:
        return 'Directories'
    filename = obj['path'].split('/')[-1]
    if '.' not in filename:
        return 'Without Extension'
    ext = filename.split('.')[-1]
    return '.' + ext



def group_by_user(obj):
    try:
        return getpwuid(os.stat(obj['path']).st_uid).pw_name
    except KeyError:
        return "User name not found"

GROUP_BY_FUNCS = {
    'e': group_by_ext,
    'u': group_by_user
}
# END GROUPING FUNCTIONALITY


def du(path, groupby=None):
    objs = get_objs_sizes(path)

    if groupby:    
        groups = group_by(objs, GROUP_BY_FUNCS[groupby])

        for key in groups:
            total_size = 0
            print(key + ':')

            for obj in groups[key]:
                total_size += obj['size']
                print(obj['path'], obj['size'])
            print('Total size: ' + str(total_size) + ' bytes')
            print('-------------------------------')

        return
    
    for obj in objs:
        print(obj['path'], obj['size'])


def main():
    args = parse_args()
    path = args.path
    du(path, args.g)

if __name__ == '__main__':
    main()