import numpy as np
import cv2
import sys
sys.path.append("./python_library")
from algorithm import FloodFill, UnionFind
import copy
import multiprocessing
import uuid
import os
import subprocess
from pathlib import Path


class PolygonDecomposer:
    DI = [0, 1, 0, -1]
    DJ = [1, 0, -1, 0]

    @staticmethod
    def draw_from_polygons(shape: tuple, geometry: list):
        """
        
        分解した多角形をもとに画像を作成
        
        """
        WHITE = (int(255), int(255), int(255))
        BLACK = (int(0), int(0), int(0))

        img = np.full(shape=shape, fill_value=255, dtype=np.uint8)
        for i, vertices in enumerate(geometry):
            for vertex in vertices:
                cv2.fillPoly(
                    img,
                    np.array([(j, i) for i, j in vertex]).reshape(1, -1, 2),
                    color=BLACK if i % 2 == 0 else WHITE
                )
        return img

    @staticmethod
    def is_polygon_inside(points_: list[tuple[float, float]], judge_point: tuple[float, float]):
        """
        
        時計回りに与えられる頂点座標からなる多角形に対して内外判定する (Winding Number Algorithm)
        
        """
        if judge_point in points_: return True
        EPS = 1E-6
        theta = 0
        points = copy.deepcopy(points_)
        points = points + [points[0]]
        x0, y0 = judge_point
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            ax, ay = x1-x0, y1-y0
            bx, by = x2-x0, y2-y0
            norms = np.hypot(ax, ay)*np.hypot(bx, by)
            cos = (ax*bx+ay*by) / norms
            if 1.0 < abs(cos) < 1.0+EPS:
                cos = 1.0 if cos > 0 else -1.0
            angle = np.arccos(cos)
            theta = theta+angle if ax*by-ay*bx<0 else theta-angle
        wn = theta / (2.0*np.pi)
        return wn > 1.0-EPS

    @classmethod
    def _extract_boundary_vertices(cls, img: np.ndarray):
        """
        
        入力された二値画像の境界を抽出する
        
        """
        to = lambda i, j: i*(img.shape[1])+j
        to_ = lambda x: (int(x/img.shape[1]), x%img.shape[1])
        uf = UnionFind(img.shape[0]*img.shape[1])
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for ii, jj in zip(cls.DI, cls.DJ):
                    ni, nj = i+ii, j+jj
                    if not 0 <= ni < img.shape[0]: continue
                    if not 0 <= nj < img.shape[1]: continue
                    if img[i, j] != img[ni, nj]: continue
                    uf.union(to(i, j), to(ni, nj))

        # 各グループを代表する座標を取得
        begins = list()
        for group in uf.all_group_members().values():
            if img[to_(min(group))] == 255: begins.append(to_(min(group)))
        
        # 境界の節点を抽出
        return [cls._extract_boundary_vertex(img, begin) for begin in begins]

    @classmethod
    def _extract_boundary_vertex(cls, img: np.ndarray, begin: tuple):
        """
        
        入力された二値画像のうち，指定された座標 (begin) を含む領域の境界を抽出する
        
        """
        # 境界を抽出する
        boundary = [begin]
        search_cnt = 0
        while True:
            bi, bj = boundary[-1]
            for k in range(4):
                i = bi+cls.DI[(search_cnt+k)%4]
                j = bj+cls.DJ[(search_cnt+k)%4]
                if not 0 <= i < img.shape[0]: continue
                if not 0 <= j < img.shape[1]: continue
                if img[i, j] == img[begin]:
                    boundary.append((i, j))
                    search_cnt = (search_cnt+k-1)%4
                    break
            if len(boundary) > 1 and boundary[0] == boundary[-1]: break

        # 境界から頂点を抽出する
        vertices = [boundary[0]]
        for k in range(1, len(boundary)-1):
            i1, j1 = boundary[k-1]
            i2, j2 = boundary[k]
            i3, j3 = boundary[k+1]
            if i1 == i2 == i3: continue
            if j1 == j2 == j3: continue
            vertices.append(boundary[k])
        return vertices

    @classmethod
    def decompose(cls, img_: np.ndarray):
        """
        
        入力された二値画像を多角形の重ね合わせに分解する

        BUG: 幅が 1px の長方形を含むときに正常動作しない → 画像を二倍して処理することにした
        TODO: OpenCV を使って輪郭抽出すれば高速化できそう → 厳密に輪郭を抽出できなかった（角近傍で近似されてしまう）
        
        """
        assert type(img_) == np.ndarray
        assert img_.dtype == np.uint8
        assert np.all((img_ == 0) | (img_ == 255))
        assert len(img_.shape) == 2 # 1 チャンネル画像
        img = img_.copy()

        # 幅が 1 の形状があると輪郭の追跡が大変だから二倍する
        img = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_NEAREST)

        # 外周を追加
        img = np.insert(img, 0, 255, axis=0)
        img = np.insert(img, img.shape[0], 255, axis=0)
        img = np.insert(img, 0, 255, axis=1)
        img = np.insert(img, img.shape[1], 255, axis=1)

        # 交互に塗りつぶしながら境界を抽出
        geometry = list()
        cnt = 0
        while True:
            tmp = img.copy()
            FloodFill.queue(
                arr=tmp,
                begin_y=0,
                begin_x=0,
                rcolor=0 if cnt % 2 == 0 else 255,
                direction=4,
            )
            diff = (255 - np.abs(img.astype(int) - tmp.astype(int))).astype(np.uint8)
            # cv2.imwrite(f"{cnt}_original.bmp", img)
            # cv2.imwrite(f"{cnt}_filled.bmp", tmp)
            # cv2.imwrite(f"{cnt}_diff.bmp", diff)
            img = tmp
            cnt += 1
            if np.array_equal(diff, np.zeros(diff.shape, dtype=np.uint8)): break
            else: geometry.append(cls._extract_boundary_vertices(diff))

        # x+ および y+ 側の境界は +2 する（ピクセル上では半開区間で表現されているがモデリング時には閉区間で形状を指定するから）
        # +1 じゃなくて +2 なのは元画像を二倍しているから
        # 外周を追加した分を差し引く
        for i in range(len(geometry)):
            for j in range(len(geometry[i])):
                shift = list()
                points = copy.deepcopy(geometry[i][j])
                points = [points[-1]] + points + [points[0]]
                for k in range(1, len(points)-1):
                    assert len(points[k]) == 2
                    i1, j1 = points[k-1]
                    i2, j2 = points[k]
                    i3, j3 = points[k+1]
                    di1, di2 = i2-i1, i3-i2
                    dj1, dj2 = j2-j1, j3-j2
                    assert (di1==0 and di2!=0 and dj1!=0 and dj2==0) or \
                        (di1!=0 and di2==0 and dj1==0 and dj2!=0)
                    shift.append((2 if dj1 < 0 or dj2 < 0 else 0, 2 if di1 > 0 or di2 > 0 else 0))
                assert len(shift) == len(geometry[i][j])
                for k in range(len(shift)):
                    ii, jj = shift[k]
                    geometry[i][j][k] = (geometry[i][j][k][0]+ii-1, geometry[i][j][k][1]+jj-1)

        # 二倍した分をもとに戻す
        for i in range(len(geometry)):
            for j in range(len(geometry[i])):
                for k in range(len(geometry[i][j])):
                    geometry[i][j][k] = [int(geometry[i][j][k][0]*0.5), int(geometry[i][j][k][1]*0.5)]

        return geometry
    
    @staticmethod
    def cxx_decompose(img: np.ndarray) -> list:
        """
        
        C++ 版の decompose

        """
        def write_img(img: np.array, path: str) -> None:
            with open(path, 'w') as f:
                H, W = img.shape
                f.write(f"{H} {W}\n")
                for h in range(H):
                    f.write(" ".join([str(img[h][w]) for w in range(W)])+"\n")


        def read_geometry(path: str) -> list:
            geometry = list()
            with open(path, 'r') as f:
                N = int(f.readline().rstrip())
                f.readline()
                for _ in range(N):
                    points_num = [int(i) for i in f.readline().rstrip().split(" ")][1:]
                    boundaries = list()
                    for n in points_num:
                        boundary = [[int(i) for i in f.readline().rstrip().split(" ")] for _ in range(n)]
                        boundaries.append(boundary)
                    geometry.append(boundaries)
                    f.readline()
            os.remove(path)
            return geometry

        assert img.dtype == np.uint8
        assert multiprocessing.current_process().name == 'MainProcess'  # 並列処理禁止

        exe_path = Path(__file__).parent / "polygon_decomposer" / "cxx_decompose.exe"
        filename = str(uuid.uuid4())
        write_img(img, path=filename)
        subprocess.call(args=[exe_path, filename])
        geometry = read_geometry(filename)
        return geometry


# if __name__ == '__main__':
#     original = cv2.imread("./polygon_decomposer/sample/small_in.bmp", cv2.IMREAD_GRAYSCALE)
#     geometry = PolygonDecomposer.decompose(original)
#     restored = PolygonDecomposer.draw_from_polygons(original.shape, geometry)
#     print(np.array_equal(original, restored))   # x+, y+ 側の座標値は +2 しているため一致しない

#     from IO import show_img
#     show_img(img=original, title="original", is_save=True)
#     show_img(img=restored, title="restored", is_save=True)

#     import matplotlib.pyplot as plt
#     from matplotlib import colors
#     for i, polygons in enumerate(geometry):
#         for polygon in polygons:
#             polygon = polygon + [polygon[0]]
#             plt.plot(
#                 [x for x, _ in polygon],
#                 [y for _, y in polygon],
#                 color=list(colors.TABLEAU_COLORS.values())[i],
#             )
#     plt.show()


if __name__ == "__main__":
    original = cv2.imread("./polygon_decomposer/sample/large_in.bmp", cv2.IMREAD_GRAYSCALE)
    geometry = PolygonDecomposer.decompose(original)
    geometry_cxx = PolygonDecomposer.cxx_decompose(original)
    assert geometry == geometry_cxx
