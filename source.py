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
        filename_num = int(filename.split('/')[-1].split('.')[0])
        temp.append([filename_num, filename])
    temp.sort()

    ret = [i[1] for i in temp]
    return ret