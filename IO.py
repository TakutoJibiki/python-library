import io, json
import numpy as np

def list_to_str(list_):
    """

    与えられたリストを文字列として返す

    Args:
        list_(list, tuple): 文字列に変換したいリスト

    Returns:
        str: リストを変換した文字列

    Notes:
        リストは入れ子にしてもいいが，入れ子の内部にはリストしか含めてはならない．
        dict や set は扱えない．

    """
    if type(list_) == str: print("str には未対応です")
    assert type(list_) in {list, tuple, np.ndarray, float, int}, '引数にはリストを指定してください'
    if type(list_) == np.ndarray: list_ = list_.tolist()

    with io.StringIO() as ios:
        print(list_, file=ios, end='')
        return ios.getvalue().replace('\'', '\"').replace('(', '[').replace(')', ']')


def str_to_list(str_):
    """

    与えられた文字列をリストとして返す

    Args:
        str_(str): リストに変換したい文字列

    Returns:
        list: 文字列を変換したリスト

    Notes:
        リストは入れ子にしてもいいが，入れ子の内部にはリストしか含めてはならない．
        dict や set は扱えない．

    """
    assert type(str_) == str, '引数には文字列を指定してください'
    ios = io.StringIO('{"tmp": ' + str_ + '}')
    return json.load(ios)["tmp"]
