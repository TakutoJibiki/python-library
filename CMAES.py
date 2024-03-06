import numpy as np
from deap import base, cma, creator


class CMAES:
    def __init__(self, obj_func, centroid, sigma, seed=42):
        """
        
        Note:
            最適解が [a, b] の範囲に存在する場合，centroid と sigma の推奨値は下記の通り
            centroid (list): [a, b] の一様乱数
            sigma (float): 0.3*(b-a)

        """
        # 乱数のシードを指定
        np.random.seed(seed)

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
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self._toolbox.register("generate", self._strategy.generate, creator.Individual)
        self._toolbox.register("update", self._strategy.update)

    def generation_step(self):
        # 新たな世代の個体群を生成
        self._population = self._toolbox.generate()

        # 個体群の評価
        self._evals = self._obj_func(np.array(self._population))
        for i, ind in enumerate(self._population):
            ind.fitness.values = self._evals[i],

        # 個体群の評価から次世代の計算のためのパラメータ更新
        self._toolbox.update(self._population)

        # 最良個体の更新
        if self._best_eval == None or self._best_eval > self.elite_eval:
            self._best_eval = self.elite_eval
            self._best_ind = self.elite_ind

    @property
    def sigma(self):
        return self._strategy.sigma
    
    @property
    def evals(self):
        return np.array(self._evals)
    
    @property
    def elite_eval(self):
        return min(self._evals)
    
    @property
    def best_eval(self):
        return self._best_eval
    
    @property
    def population(self):
        if self._population == None: return None
        return np.array([[i for i in ind] for ind in self._population])
    
    @property
    def elite_ind(self):
        return self.population[np.argmin(self._evals)]
    
    @property
    def best_ind(self):
        return np.array(self._best_ind)


if __name__ == "__main__":
    def obj_func(args):
        ret = list()
        for x, y in args:
            ret.append((x-3)**2 + (y+1)**2)
        return ret

    cmaes = CMAES(
        obj_func=obj_func,
        centroid=[0]*2,
        sigma=0.3*(5-(-5)),
    )
    
    while cmaes.sigma > 1E-3:
        cmaes.generation_step()
        print(f'{cmaes.elite_eval} | {cmaes.elite_ind}')
    print(f'{cmaes.best_eval} | {cmaes.best_ind}')
