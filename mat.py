import scipy.io 
import numpy as np
import argparse
import cbor2
import os
from pathlib import Path

VERSION = "1.1.0"

def read_mat_file(file_path):
    data = scipy.io.loadmat(file_path)
    return data
"""
def write_bin_file(data, bin_file_path):
    with open(bin_file_path, 'wb') as bin_file:
        def write_array(array):
            if isinstance(array, np.ndarray):
                if array.size == 0:
                    return
                if array.dtype.kind in ('u', 'i', 'f'):
                    array.ravel().tofile(bin_file)
                elif array.dtype.kind == 'O':
                    for item in np.nditer(array, flags=['refs_ok'], op_flags=['readonly']):
                        if isinstance(item[()], np.ndarray):
                            write_array(item[()])
                        elif isinstance(item[()], (int, float, np.number)):
                            np.array([item[()]]).ravel().tofile(bin_file)
        for key, value in data.items():
            if key[0] != '_':
                write_array(value)
"""
def write_bin_file(data, bin_file_path):
    with open(bin_file_path, 'wb') as bin_file:
        def serialize_array(array):
            if isinstance(array, np.ndarray):
                if array.size == 0:
                    return None
                if array.dtype.kind in ('u', 'i', 'f'):
                    return array.ravel().tolist()
                elif array.dtype.kind == 'O':
                    return [serialize_array(item[()]) for item in np.nditer(array, flags=['refs_ok'], op_flags=['readonly'])]
            elif isinstance(array, (int, float, np.number)):
                return array
            return None
        serialized_data = {key: serialize_array(value) for key, value in data.items() if key[0] != '_'}
        cbor2.dump(serialized_data, bin_file)
        
def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mat"):
                mat_file_path = Path(root) / file
                cbor_file_path = mat_file_path.with_suffix('.cbor')
                mat_data = read_mat_file(str(mat_file_path))
                write_bin_file(mat_data, str(cbor_file_path))
                print(f"Файл {file} обработан и сохранен как {cbor_file_path.name}")
       
def main():
    parser = argparse.ArgumentParser(description="Чтение mat и сохранение его в бинарном формате")
    parser.add_argument('-help', action='help', default=argparse.SUPPRESS, help='Показать это сообщение и выйти')
    parser.add_argument('-path_to_mat_file', type=str, required=True, help='Путь к MAT файлу или директории с файлами MAT')
    parser.add_argument('-path_to_save_binmat_file', type=str, required=True, help='Путь для сохранения .cbor файла (используется, когда необходимо сохранить только один файл)')
    parser.add_argument('-all', action='store_true', help='Обработать все файлы MAT в указанной директории')
        
    args = parser.parse_args()
    """"
    mat_data = read_mat_file(args.path_to_mat_file)
    write_bin_file(mat_data, args.path_to_save_binmat_file)
    print("Файл успешно сохранен в: ", args.path_to_save_binmat_file)
    """
    if args.all:
        if os.path.isdir(args.path_to_mat_file):
            process_directory(args.path_to_mat_file)
        else:
            print("Указанный путь не является директорией")
    else:
        if os.path.isfile(args.path_to_mat_file):
            mat_data = read_mat_file(args.path_to_mat_file)
            cbor_file_path = args.path_to_save_binmat_file if args.path_to_save_binmat_file else args.path_to_mat_file.replace('.mat', '.cbor')
            write_bin_file(mat_data, cbor_file_path)
            print(f"Файл успешно сохранен в: {cbor_file_path}")
        else:
            print("Указаныый MAT файл не найден")
        
if __name__ == '__main__':
    main()