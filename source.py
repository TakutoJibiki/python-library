import glob, os

def sort_filename(filenames):
    """
    
    連番のファイル名を数値の昇順にソートする

    Note:
        0.csv, 1.csv, ..., 10.csv の場合，文字列のままソートすると
        0, 1, 10, ... となってしまい，ファイル名の数値の順にならない．
        そこで，本メソッドを使えば数値の昇順にソートすることができる．
    
    """
    temp = []
    for filename in filenames:
        if '\\' in filename:
            filename_num = int(filename.split('\\')[-1].split('.')[0])
            temp.append([filename_num, filename])
        elif '/' in filename:
            filename_num = int(filename.split('/')[-1].split('.')[0])
            temp.append([filename_num, filename])
    temp.sort()

    ret = [i[1] for i in temp]
    return ret


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
        separator = '\\' if '\\' in file else '/'
        pre = separator.join(file.split(separator)[:-1])
        extention = file.split('.')[-1]
        os.rename(src=file, dst=f'{pre}{separator}#{cnt}.{extention}')
        cnt += 1

    for file in glob.glob(f'{directory}/*'):
        assert '#' in file
        os.rename(src=file, dst=file.replace('#', ''))
