import glob, os
from PIL import Image
from glob import glob
import pandas as pd
import shutil
import matplotlib.pyplot as plt

class File:
    @staticmethod
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

    @staticmethod
    def rename(directory, start_index):
        """
        
        指定した番号スタートの連番にリネーム

        Args:
            directory (str): リネームするファイルが含まれるディレクトリのパス
            start_index (int): 連番の最初の番号
        
        """
        cnt = start_index
        for file in File.sort_filename(glob.glob(f'{directory}/*')):
            assert not '#' in file
            pre = os.path.dirname(file)
            ext = os.path.splitext(file)[-1]
            os.rename(src=file, dst=f'{pre}{os.path.sep}#{cnt}{ext}')
            cnt += 1

        for file in glob.glob(f'{directory}/*'):
            assert '#' in file
            os.rename(src=file, dst=file.replace('#', ''))

    @staticmethod
    def mkdir(path, delete=True):
        """
        
        ディレクトリが存在していたら削除して作り直す
        
        """
        if os.path.isdir(path):
            if delete:
                shutil.rmtree(path)
                os.makedirs(path)
        else:
            os.makedirs(path)


class Gif:
    @staticmethod
    def make_gif(dir, gif_name, sampling=1, duration=100):
        assert type(sampling) == int

        files = File.sort_filename(glob(f'{dir}/*.png'))
        files = [files[i] for i in range(0, len(files), sampling)]  # サンプリング

        images = list(map(lambda file : Image.open(file) , files))
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop = 0,
        )

    @staticmethod
    def make_gif_from_csv(csv_path, gif_name, header=None, labels=None, marker=None, sampling=1, duration=100):
        """make_gif_from_csv
        
        指定した CSV からプロットのアニメーション GIF を生成する
        
        """
        table = pd.read_csv(csv_path, header=header).values

        assert not os.path.isdir('tmp')
        os.makedirs('tmp')

        min_x = min(table[:, 0])
        max_x = max(table[:, 0])
        min_y = min(table[:, 1])
        max_y = max(table[:, 1])
        plt.rcParams['font.size'] = 12
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['mathtext.fontset'] = 'cm'
        for i in range(table.shape[0]):
            plt.cla()
            plt.clf()
            plt.xlim(min_x*1.1, max_x*1.1)
            plt.ylim(min_y*1.1, max_y*1.1)
            plt.xlabel(labels[0])
            plt.ylabel(labels[1])
            plt.plot(table[:i+1, 0], table[:i+1, 1], marker=marker)
            plt.savefig(f'tmp/{i}.png')

        Gif.make_gif('tmp', gif_name, sampling, duration)
        shutil.rmtree('tmp')


if __name__ == '__main__':
    Gif.make_gif(dif='tmp', gif_name='anim.gif')
    # Gif.make_gif_from_csv(csv_path='4500.csv', gif_name='anim.gif', header=0, labels=['$H$', '$B$'], duration=300, marker='')
