from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque


class UnionFind:
    """
    
    https://note.nkmk.me/python-union-find/
    
    """
    def __init__(self, n):
        self.n = n
        self.parents = [-1] * n

    def find(self, x):
        if self.parents[x] < 0:
            return x
        else:
            self.parents[x] = self.find(self.parents[x])
            return self.parents[x]

    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)

        if x == y:
            return

        if self.parents[x] > self.parents[y]:
            x, y = y, x

        self.parents[x] += self.parents[y]
        self.parents[y] = x

    def size(self, x):
        return -self.parents[self.find(x)]

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def members(self, x):
        root = self.find(x)
        return [i for i in range(self.n) if self.find(i) == root]

    def roots(self):
        return [i for i, x in enumerate(self.parents) if x < 0]

    def group_count(self):
        return len(self.roots())

    def all_group_members(self):
        group_members = defaultdict(list)
        for member in range(self.n):
            group_members[self.find(member)].append(member)
        return group_members

    def __str__(self):
        return '\n'.join(f'{r}: {m}' for r, m in self.all_group_members().items())


class FloodFill:
    @staticmethod
    def _gif_init():
        fig = plt.figure(figsize=(4,4))
        ax = plt.gca()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        imgs = []
        return fig, imgs
    
    @staticmethod
    def _gif_add(imgs: list, arr: np.ndarray):
        img = plt.imshow(arr.T, animated=True)
        imgs.append([img])

    @staticmethod
    def _gif_save(fig, imgs: list, filename: str):
        ani = animation.ArtistAnimation(fig, imgs)
        ani.save(filename, writer="imagemagick")

    @staticmethod
    def stack(arr: np.ndarray, begin_y: int, begin_x: int, rcolor: int,
            direction: int, filename: str = None):
        """

        FloodFill のスタックによる実装（開始位置に隣接する同色のマスを rcolor に塗りつぶす）．

        Args:
            arr (np.ndarray): 塗りつぶしを行う対象の二次元配列
            begin_y (int): 塗りつぶし開始マスの行
            begin_x (int): 塗りつぶし開始マスの列
            rcolor (int): 塗りつぶす色 (replacement-color)
            direction (int): 接続されているとみなす方向 (4 or 8)
            filename (str): 途中経過のアニメーションの保存パス．未指定の場合はアニメーション画像は保存されない．

        Notes:
            入力配列が大きすぎるとスタックオーバーフローが発生する可能性あり．

        """
        def execute_fill(arr, begin_y, begin_x, tcolor, rcolor, direction):
            if not arr[begin_y, begin_x] == tcolor: return
            arr[begin_y, begin_x] = rcolor
            if filename: FloodFill._gif_add(imgs=imgs, arr=arr)
            dxs = [1, 0, -1, 0, 1, -1, -1, 1]
            dys = [0, 1, 0, -1, 1, 1, -1, -1]
            for dx, dy in zip(dxs[:direction], dys[:direction]):
                nx = begin_x + dx
                ny = begin_y + dy
                if 0 <= nx < arr.shape[1] and 0 <= ny < arr.shape[0]:
                    execute_fill(arr, ny, nx, tcolor, rcolor, direction)

        assert direction in [4, 8], "direction must be 4 or 8."
        tcolor = arr[begin_y, begin_x]
        if tcolor == rcolor: return
        if filename: fig, imgs = FloodFill._gif_init()
        execute_fill(arr, begin_y, begin_x, tcolor, rcolor, direction)
        if filename: FloodFill._gif_save(fig=fig, imgs=imgs, filename=filename)

    @staticmethod
    def queue(arr: np.ndarray, begin_y: int, begin_x: int, rcolor: int,
              direction: int, filename: str = None):
        """

        FloodFill のキューによる実装（開始位置に隣接する同色のマスを rcolor に塗りつぶす）．

        Args:
            arr (np.ndarray): 塗りつぶしを行う対象の二次元配列
            begin_y (int): 塗りつぶし開始マスの行
            begin_x (int): 塗りつぶし開始マスの列
            rcolor (int): 塗りつぶす色 (replacement-color)
            direction (int): 接続されているとみなす方向 (4 or 8)
            filename (str): 途中経過のアニメーションの保存パス．未指定の場合はアニメーション画像は保存されない．

        """
        assert direction in [4, 8], "direction must be 4 or 8."
        tcolor = arr[begin_y, begin_x]
        if tcolor == rcolor: return
        if filename: fig, imgs = FloodFill._gif_init()
        q = deque()
        q.append((begin_y, begin_x))
        arr[begin_y, begin_x] = rcolor
        while q:
            y, x = q.popleft()
            dxs = [1, 0, -1, 0, 1, -1, -1, 1]
            dys = [0, 1, 0, -1, 1, 1, -1, -1]
            for dx, dy in zip(dxs[:direction], dys[:direction]):
                nx = x + dx
                ny = y + dy
                if not 0 <= nx < arr.shape[1]: continue
                if not 0 <= ny < arr.shape[0]: continue
                if arr[ny, nx] != tcolor: continue
                arr[ny, nx] = rcolor
                q.append((ny, nx))
                if filename: FloodFill._gif_add(imgs=imgs, arr=arr)
        if filename: FloodFill._gif_save(fig=fig, imgs=imgs, filename=filename)


if __name__ == '__main__':
    arr = np.array([[1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,0,0,0,1],
                    [1,0,0,0,1,0,0,0,0,0,1],
                    [1,0,0,1,1,1,0,0,0,0,1],
                    [1,1,1,1,0,0,1,1,0,0,1],
                    [1,0,0,0,0,1,0,0,0,0,1],
                    [1,0,0,0,1,0,0,0,0,0,1],
                    [1,0,0,0,1,0,0,0,0,0,1],
                    [1,0,1,1,1,1,1,1,1,1,1]])

    FloodFill.queue(arr, 8, 1, rcolor=2, direction=4, filename='flood_fill.gif')
