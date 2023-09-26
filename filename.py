import glob, os

def sort_filename(filenames):
    """
    
    連番のファイル名を数値の昇順にソートする

    Args:
        filenames (list): 複数のファイル名からなるリスト

    Note:
        0.csv, 1.csv, ..., 10.csv の場合，文字列のままソートすると
        0, 1, 10, ... となってしまい，ファイル名の数値の順にならない．
        そこで，本メソッドを使えば数値の昇順にソートすることができる．
    
    """
    temp = []
    for filename in filenames:
        assert '.' in filename
        filename_num = int(os.path.basename(filename).split('.')[0])
        temp.append([filename_num, filename])
    temp.sort()
    return [i[1] for i in temp]


def rename(directory, start_index):
    """
    
    指定した番号スタートの連番にリネーム

    Args:
        directory (str): リネームするファイルが含まれるディレクトリのパス
        start_index (int): 連番の最初の番号
    
    """
    cnt = start_index
    for file in sort_filename(glob.glob(f'{directory}/*')):
        assert not '#' in file
        pre = os.path.dirname(file)
        ext = os.path.splitext(file)[-1]
        os.rename(src=file, dst=f'{pre}{os.path.sep}#{cnt}{ext}')
        cnt += 1

    for file in glob.glob(f'{directory}/*'):
        assert '#' in file
        os.rename(src=file, dst=file.replace('#', ''))
