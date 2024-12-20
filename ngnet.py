import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import cv2
import math


# TODO: ngnet = NGnet([NGnet.Basis(mux=mux, muy=muy, r=STDEV) for mux, muy in BASIS_MUS]) の形で楽できるようにコンストラクタを修正
class NGnet:
    def __init__(
            self,
            grid: list[np.ndarray, np.ndarray],
            basis_num: int,
            symmetry: bool=False,
        ):
        """
        
        Args:
            grid (list[np.ndarray, np.ndarray]): 形状関数を計算する座標 (np.meshgrid)
            basis_num (int): 基底の数
            symmetry (bool): 回転対称の制約を課すか

        Note:
            grid は格子の頂点の座標ではなく形状関数を計算する座標値
        
        """
        self.grid_x, self.grid_y = grid
        self.basis_num = basis_num
        self.symmetry = symmetry

        assert type(self.grid_x) == type(self.grid_y) == np.ndarray
        assert len(self.grid_x.shape) == 2
        assert self.grid_x.shape == self.grid_y.shape

    def __gaussian_2d(self, pos: list[float, float], r: list[float, float], theta: float):
        # X, Y は二次元配列
        X, Y = self.grid_x, self.grid_y
        input_shape = X.shape
        mu_x, mu_y = pos
        sx, sy = r

        # 定数の計算
        mu = np.array([[mu_x], [mu_y]])
        diag = np.diag([sx**2, sy**2])
        eigen_mat = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)],
        ])
        cov = eigen_mat@diag@(eigen_mat.T)
        cov_inv = np.linalg.inv(cov)
        coef = 1/(2*np.pi*np.sqrt(np.linalg.det(cov)))

        # 入力に次元を合わせる
        mu = np.full(input_shape+(2, 1), mu)
        cov_inv = np.full(input_shape+(2, 2), cov_inv)

        # ガウス関数を計算
        pos = np.array([[X], [Y]]).transpose(2, 3, 0, 1) - mu
        pos_t = pos.transpose(0, 1, 3, 2)
        ret = coef * np.exp(-0.5*pos_t@cov_inv@pos)
        return ret.reshape(input_shape)

    def get_dist(
        self,
        weights: list[float],
        poss: list[list[float, float]],
        rs: (list[list[float, float]]),
        thetas: list[float],
    ):
        """

        Args:
            weights (list[float]): 基底関数の重み (w1, w2, ...)
            poss (list[list[flota, float]]): 基底関数の中心 ((mux1, muy1), (mux2, muy2), ...)
            rs (list[list[flota, float]]): 基底関数の標準偏差 ((sx1, sy1), (sx2, sy2), ...)
            thetas (list[float]): 基底の楕円の角度 [rad] (theta1, theta2, ...)                    
                
        """
        assert self.basis_num == len(weights) == len(poss) == len(rs) == len(thetas)

        # TODO: 行列計算に対応させる
        gauss = [self.__gaussian_2d(pos=pos, r=r, theta=theta) \
                 for pos, r, theta in zip(poss, rs, thetas)]
        gauss_sum = sum(gauss)
        normalized = [g/gauss_sum for g in gauss]
        shape_func = sum([w*b for w, b in zip(weights, normalized)])
        dist = np.zeros(shape_func.shape, dtype=np.uint8)
        for i in range(shape_func.shape[0]):
            for j in range(shape_func.shape[1]):
                dist[i][j] = (shape_func[i][j] >= 0)*1.0
        
        if self.symmetry:
            tmp = cv2.rotate(dist, cv2.ROTATE_180)
            dist = np.concatenate([dist, tmp])

        return dist
    
    def plot_basis(
        self,
        poss: list[list[float, float]],
        rs: (list[list[float, float]]),
        thetas: list[float],
        filename: str,
    ):
        assert self.basis_num == len(poss) == len(rs) == len(thetas)

        plt.cla(), plt.clf()
        ax = plt.axes()
        for i in range(self.basis_num):
            ax.add_patch(Ellipse(
                xy=poss[i],
                width=rs[i][0]*2,   # 楕円の“直径”
                height=rs[i][1]*2,
                angle=math.degrees(thetas[i]),
                ec="red",
                fill=False,
            ))
        plt.scatter([x for x, _ in poss], [y for _, y in poss], s=5, color='black')

        x_min, x_max = np.min(self.grid_x), np.max(self.grid_x)
        y_min, y_max = np.min(self.grid_y), np.max(self.grid_y)
        plt.plot(
            [x_min, x_max, x_max, x_min, x_min],
            [y_min, y_min, y_max, y_max, y_min],
            color="black",
        )
        plt.axis("square")
        plt.savefig(filename)
        plt.cla(), plt.clf()


if __name__ == '__main__':
    np.random.seed(43)

    steps = np.arange(start=-10, stop=10, step=0.1)
    grid = np.meshgrid(steps, steps)
    poss = list()
    for x in range(-8, 10, 2):
        for y in range(-8, 10, 2):
            poss += [[x, y]]
    basis_num = len(poss)

    rs = np.random.rand(basis_num*2).reshape((basis_num, 2))*3
    thetas = np.random.rand(basis_num)*math.pi*2

    ngnet = NGnet(
        grid=grid,
        basis_num=basis_num,
        symmetry=False,
    )

    dist = ngnet.get_dist(
        weights=np.random.rand(basis_num)*2-1,
        poss=poss,
        rs=rs,
        thetas=thetas,
    )

    ngnet.plot_basis(poss=poss, rs=rs, thetas=thetas, filename="basis.png")

    plt.contourf(grid[0], grid[1], dist)
    plt.axis('square')
    plt.grid()
    plt.savefig("dist.png")
