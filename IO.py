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


def show_img(img: np.array, title: str, is_save: bool = False):
    """
    
    np.array 形式の画像を matplotlib で出力する

    """
    import matplotlib.pyplot as plt
    plt.cla()
    plt.clf()

    plt.imshow(img)
    max_y, max_x = img.shape[0]-0.5, img.shape[1]-0.5
    min_y, min_x = -0.5, -0.5
    plt.ylim(min_y-0.5, max_y+0.5)
    plt.xlim(min_x-0.5, max_x+0.5)
    if max(img.shape) < 30:
        plt.yticks(np.linspace(start=min_y, stop=max_y, num=img.shape[0]+1))
        plt.xticks(np.linspace(start=min_x, stop=max_x, num=img.shape[1]+1), rotation=90)
    plt.gca().invert_yaxis()
    plt.grid()

    if is_save: plt.savefig(f"{title}.png")
    else: plt.show()

    plt.close()
