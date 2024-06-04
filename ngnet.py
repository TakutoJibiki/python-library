import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
import numpy as np


# TODO: ngnet = NGnet([NGnet.Basis(mux=mux, muy=muy, r=STDEV) for mux, muy in BASIS_MUS]) の形で楽できるようにコンストラクタを修正
class NGnet:
    class Basis:
        def __init__(self, mux: float, muy: float, r: float = None,
                     sx: float = None, sy: float = None, theta: float = None):
            """
            
            Note:
                theta の単位は [rad]
            
            """
            self.mux = mux
            self.muy = muy
            self.sx = sx
            self.sy = sy
            self.theta = theta

            if any(i is None for i in [sx, sy, theta]):
                assert r is not None
                self.sx = self.sy = r
                self.theta = 0
            if r is None:
                assert all(i is not None for i in [sx, sy, theta])

        def gaussian_2d(self, X: np.ndarray, Y: np.ndarray):
            # X, Y は二次元配列
            assert type(X) == type(Y) == np.ndarray
            assert len(X.shape) == 2
            assert X.shape == Y.shape
            input_shape = X.shape

            # 定数の計算
            mu = np.array([[self.mux], [self.muy]])
            diag = np.diag([self.sx**2, self.sy**2])
            eigen_mat = np.array([
                [np.cos(self.theta), -np.sin(self.theta)],
                [np.sin(self.theta), np.cos(self.theta)],
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

        @staticmethod
        def randomly_generate(x_range: tuple, y_range: tuple):
            """ 

            基底関数のパラメータをランダムに生成

            """
            assert all([a < b for a, b in [x_range, y_range]])  # 乱数生成の範囲
            generate = lambda ranges: [np.random.rand()*(b-a)+a for a, b in ranges]
            mux, muy, sx, sy, theta = generate([
                [x_range[0], x_range[1]],               # mux
                [y_range[0], y_range[1]],               # muy
                [1E-3, (x_range[1]-x_range[0])*0.5],    # sx
                [1E-3, (y_range[1]-y_range[0])*0.5],    # sy
                [0, np.pi],                             # theta
            ])
            return NGnet.Basis(mux=mux, muy=muy, sx=sx, sy=sy, theta=theta)

    def __init__(self, bases: list[Basis], grid: tuple[np.ndarray, np.ndarray]):
        self.bases = bases
        self.grid = grid    # numpy の meshgrid の (X, Y)

    def get_dist(self, weights: list):
        # TODO: 行列計算に対応させる
        # TODO: 厳密には要素の中心で形状関数を計算できていない
        gauss = [basis.gaussian_2d(self.grid[0], self.grid[1]) for basis in self.bases]
        gauss_sum = sum(gauss)
        normalized = [g/gauss_sum for g in gauss]
        shape_func = sum([w*b for w, b in zip(weights, normalized)])
        dist = np.zeros(shape_func.shape, dtype=np.uint8)
        for i in range(shape_func.shape[0]):
            for j in range(shape_func.shape[1]):
                dist[i][j] = (shape_func[i][j] >= 0)*1.0
        return dist

    @staticmethod
    def plot(X: np.ndarray, Y: np.ndarray, bases: Basis,
             shape_bin: np.ndarray, filename: str = None):
        x_min, x_max = np.min(X), np.max(X)
        y_min, y_max = np.min(Y), np.max(Y)
        def plot_common(ax):
            ax.plot(
                [x_min, x_min, x_max, x_max, x_min],
                [y_min, y_max, y_max, y_min, y_min],
                color='black',
                lw=1,
            )
            ax.axis('square')
            x_margin = (x_max-x_min)*0.1
            y_margin = (y_max-y_min)*0.1
            ax.set_xlim(x_min-x_margin, x_max+x_margin)
            ax.set_ylim(y_min-y_margin, y_max+y_margin)
            ax.set_xticks([])
            ax.set_yticks([])
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(False)
            plt.gca().spines['left'].set_visible(False)

        fig = plt.figure(figsize=(3, 5.5))
        ax_basis = plt.subplot(2, 1, 1)
        for basis in bases:
            ax_basis.scatter(basis.mux, basis.muy, color='black', s=10)
            ax_basis.add_patch(patches.Ellipse(
                xy=(basis.mux, basis.muy),
                width=basis.sx*2,   # 楕円の「直径」
                height=basis.sy*2,
                angle=basis.theta*180/np.pi,
                fill=None,
                ec='red',
            ))
        plot_common(ax_basis)
        ax_shape = plt.subplot(2, 1, 2)
        ax_shape.contourf(X, Y, shape_bin, cmap=cm.Greens)
        plot_common(ax_shape)

        plt.subplots_adjust(hspace=-0.01)
        if filename is None: plt.show()
        else: plt.savefig(filename, dpi=300)
        plt.close()
        plt.cla()
        plt.clf()


if __name__ == '__main__':
    np.random.seed(42)

    def basic_sample():
        # 位置と半径を固定
        X = np.arange(-15E-3, 15E-3+0.075E-3-0.001E-3, 0.075E-3)
        Y = np.arange(12E-3, 44.4E-3+0.075E-3-0.001E-3, 0.075E-3)
        STDEV = 0.003850402576354841
        BASIS_MUS = [[-0.013,0.014], [-0.013,0.01968], [-0.013,0.02536], [-0.013,0.031039999999999998], [-0.013,0.03672], [-0.013,0.0424], [-0.0078,0.014], [-0.0078,0.01968], [-0.0078,0.02536], [-0.0078,0.031039999999999998], [-0.0078,0.03672], [-0.0078,0.0424], [-0.0026,0.014], [-0.0026,0.01968], [-0.0026,0.02536], [-0.0026,0.031039999999999998], [-0.0026,0.03672], [-0.0026,0.0424], [0.0026,0.014], [0.0026,0.01968], [0.0026,0.02536], [0.0026,0.031039999999999998], [0.0026,0.03672], [0.0026,0.0424], [0.0078,0.014], [0.0078,0.01968], [0.0078,0.02536], [0.0078,0.031039999999999998], [0.0078,0.03672], [0.0078,0.0424], [0.013,0.014], [0.013,0.01968], [0.013,0.02536], [0.013,0.031039999999999998], [0.013,0.03672], [0.013,0.0424]]
        grid = np.meshgrid(X, Y)
        bases = [NGnet.Basis(mux=mux, muy=muy, r=STDEV) for mux, muy in BASIS_MUS]
        ngnet = NGnet(bases=bases, grid=grid)
        dist = ngnet.get_dist(weights=[np.random.rand()*10-5 for _ in range(len(bases))])
        NGnet.plot(X=grid[0], Y=grid[1], bases=bases, shape_bin=dist)

    def generalized_sample():
        # 位置を半径を可変（一般化）
        DESIGN_SIZE = 10
        X = np.arange(-DESIGN_SIZE, DESIGN_SIZE+0.1, 0.1)
        Y = np.arange(-DESIGN_SIZE, DESIGN_SIZE+0.1, 0.1)
        grid = np.meshgrid(X, Y)
        bases = [NGnet.Basis.randomly_generate(
            x_range=[-DESIGN_SIZE, DESIGN_SIZE],
            y_range=[-DESIGN_SIZE, DESIGN_SIZE],
        ) for _ in range(9)]
        weights = [1, 2,-3,-4,-5,-6, 7, 8, 7]
        ngnet = NGnet(bases=bases, grid=grid)
        dist = ngnet.get_dist(weights=weights)
        NGnet.plot(X=grid[0], Y=grid[1], bases=bases, shape_bin=dist)

    # basic_sample()
    generalized_sample()
    