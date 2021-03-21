import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Путь до директории')

    return parser.parse_args()


def get_dir_size(path):
    total_size = 0
    for obj in os.scandir(path):
        if obj.is_file():
            total_size += obj.stat().st_size
        elif obj.is_dir():
            total_size += get_dir_size(obj.path)
    
    return total_size


def du(path):
    for dirpath, dirnames, filenames in os.walk(path):
        dir_size = get_dir_size(dirpath)
        print(dir_size, dirpath)
    


def main():
    args = parse_args()
    path = args.path
    tree = os.walk(path)
    du(path)

if __name__ == '__main__':
    main()