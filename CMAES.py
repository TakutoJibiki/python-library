import numpy as np
from deap import base, cma, creator
import copy


class CMAES:
    def __init__(self, obj_func, centroid: list, sigma: float):
        """
        
        CMA-ES で obj_func を最大化する ind を探す．
        最小化問題を解きたい場合はマイナスをかけて目的関数を定義する．

        Args:
            obj_func (function): 最大化する目的関数．複数の個体を同時に受け取れるように実装する．以下に例を示す．
                def obj_func(args):
                    return [-((x-3)**2 + (y+1)**2) for x, y in args]
            centroid (list): 探索範囲の中心（共分散行列の平均ベクトル）の初期値．
            sigma (float): ステップサイズの初期値．

        Note:
            最適解が [a, b] の範囲に存在する場合，centroid と sigma の推奨値は下記の通り
            centroid (list): [a, b] の一様乱数
            sigma (float): 0.3*(b-a)

        """
        # メンバの設定
        self._obj_func = obj_func
        self._population = None
        self._best_eval = None
        self._best_ind = None

        # アルゴリズム初期化
        self._strategy = cma.Strategy(
            centroid=np.array(centroid),
            sigma=sigma,
        )

        # 設定
        self._toolbox = base.Toolbox()
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self._toolbox.register("generate", self._strategy.generate, creator.Individual)
        self._toolbox.register("update", self._strategy.update)

    def generation_step(self):
        # 新たな世代の個体群を生成
        self._population = self._toolbox.generate()

        # 個体群の評価
        self._evals = self._obj_func(self.population)
        for i, ind in enumerate(self._population):
            ind.fitness.values = self._evals[i],

        # 個体群の評価から次世代の計算のためのパラメータ更新
        self._toolbox.update(copy.deepcopy(self._population))

        # 最良個体の更新
        if self._best_eval == None or self._best_eval < self.elite_eval:
            self._best_eval = self.elite_eval
            self._best_ind = self.elite_ind

    @property
    def sigma(self):
        return self._strategy.sigma
    
    @property
    def population(self):
        """

        Note:
            <class 'deap.creator.Individual'> を list に変換する．
            変換前：
                [<class 'deap.creator.Individual'>, <class 'deap.creator.Individual'>, ...]
            変換後：
                [list, list, ...]

        """
        if self._population == None: return None
        return [[i for i in ind] for ind in self._population]

    @property
    def elite_eval(self):
        return max(self._evals)
    
    @property
    def best_eval(self):
        return self._best_eval
    
    @property
    def elite_ind(self):
        fits = [ind.fitness for ind in self._population]
        elite_id = fits.index(max(fits))
        return [i for i in self._population[elite_id]]
    
    @property
    def best_ind(self):
        return self._best_ind


if __name__ == "__main__":
    # 目的関数
    def obj_func(args):
        return [-((x-3)**2 + (y+1)**2) for x, y in args]
    
    # 乱数のシードを指定
    np.random.seed(42)

    cmaes = CMAES(
        obj_func=obj_func,
        centroid=[0]*2,
        sigma=0.3*(5-(-5)),
    )
    
    for gen in range(50):
        cmaes.generation_step()
        print(
            f'\rGen. {format(gen+1, "0>3")}  |  ' +
            '{:.3e}  |  '.format(cmaes.elite_eval) +
            f'{cmaes.elite_ind}'
        )
    print(f'{cmaes.best_eval} | {cmaes.best_ind}')
