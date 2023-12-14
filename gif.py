from PIL import Image
from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
import os, shutil
from filename import sort_filename

def make_gif(dir, gif_name, sampling=1, duration=100):
    assert type(sampling) == int

    files = sort_filename(glob(f'{dir}/*.png'))
    files = [files[i] for i in range(0, len(files), sampling)]  # サンプリング

    images = list(map(lambda file : Image.open(file) , files))
    images[0].save(
        gif_name,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop = 0,
    )


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

    make_gif('tmp', gif_name, sampling, duration)
    shutil.rmtree('tmp')


if __name__ == '__main__':
    make_gif(dif='tmp', gif_name='anim.gif')
    # make_gif_from_csv(csv_path='4500.csv', gif_name='anim.gif', header=0, labels=['$H$', '$B$'], duration=300, marker='')
