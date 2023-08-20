from PIL import Image
from glob import glob

def make_gif(dir, gif_name, sampling=1, duration=100):
    assert type(sampling) == int

    # 拡張子
    files = glob(f'{dir}/*')
    ext = files[0].split('.')[-1]

    # サンプリング
    files = [f'{dir}/{i}.{ext}' for i in range(len(files)) if i%sampling==0]

    images = list(map(lambda file : Image.open(file) , files))
    images[0].save(
        gif_name,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop = 0,
    )
