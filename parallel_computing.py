"""

1. 並列処理したい処理を func() として定義
2. パラメータを指定（VERBOSE, MAX_PROCESS_NUM 等）
3. 別のファイルから multi_exec() を呼び出す

"""
import traceback
from multiprocessing import Pool
import pickle
import subprocess, os


VERBOSE = True          # 経過の出力
MAX_PROCESS_NUM = 8
COM_FILE = "com.bin"


def func(arg):
    return arg**2


def pickle_write(arg):
    with open(COM_FILE, 'wb') as p:
        pickle.dump(arg, p)


def pickle_read():
    with open(COM_FILE, 'rb') as p:
        result = pickle.load(p)
    os.remove(COM_FILE)
    return result


def wrapper(process_num, query):
    if not query: return []
    result = []
    for i, arg in enumerate(query):
        result.append(func(arg))
        if VERBOSE and process_num == 0:
            print("\r" + "\t"*8 + f'{i+1} / {len(query)} ', end="\r")
    return result


def handler():
    # 引数受け取り
    query = pickle_read()

    # 空のデータが送られてきたら即返す
    if not query:
        pickle_write([])
        return

    processes = []
    pool = Pool()
    process_num = [len(query) // MAX_PROCESS_NUM for _ in range(MAX_PROCESS_NUM)]
    for i in range(len(query) % MAX_PROCESS_NUM): process_num[i] += 1

    # 並列に実行
    for i in range(MAX_PROCESS_NUM):
        start = sum(process_num[:i])
        end = sum(process_num[:i+1])
        p = pool.apply_async(wrapper, args=[i, query[start:end]])
        processes.append(p)

    # 各プロセスの終了を順番に待つ
    result = []
    while processes:
        if processes and processes[0].ready():
            result += processes[0].get()
            processes.pop(0)

    pickle_write(result)


def multi_exec(args, python3=False):
    pickle_write(args)
    py = "python"
    if python3: py += "3"
    subprocess.run([py, __file__])
    return pickle_read()


if __name__ == '__main__':
    try:
        handler()
    except SystemExit:
        pass
    except:
        print(traceback.format_exc())
