import numpy as np
from deap import base, cma, creator
import copy


class CMAES:
    def __init__(self,
                 obj_func,
                 search_intervals: list,
                 constraints: list = None,
                 penalty: float = None,
                 lambda_: int = None):
        """
        
        CMA-ES で obj_func を最大化する ind を探す．
        最小化問題を解きたい場合はマイナスをかけて目的関数を定義する．

        Args:
            obj_func (function): 最大化する目的関数．複数の個体を同時に受け取れるように実装する．以下に例を示す．
                def obj_func(args):
                    return [-((x-3)**2 + (y+1)**2) for x, y in args]
            search_intervals (list): 重点的に探索する範囲 [a_i, b_i]^n．以下に例を示す．
                [
                    [a_1, b_1],
                    [a_2, b_2],
                    ...
                ]
            constraints (list): 制約範囲の上下限からなるリスト．制約を指定しない次元には "None" を指定する．
                ex: [(x1_l, x1_h), (x2_l, x2_h), None, ...]
            penalty (float): 制約違反時のペナルティのベース．実際にはこの値に違反量を加算してペナルティとする．制約を満たす範囲での最悪の評価値を指定すればよい．
            lambda_ (int): 集団サイズ．何も指定しなかったら int(4+3*ln(N)) が指定される．

        Note:
            CMA-ES 中での正規化は search_intervals の値に基づく

        """
        # エラーチェック
        for a, b in search_intervals: assert a < b
        assert (constraints is None and penalty is None) \
            or (constraints is not None and penalty is not None)

        # デフォルト値
        if constraints is None: constraints = [None] * len(search_intervals)
        else: assert len(search_intervals) == len(constraints)
        if lambda_ is None: lambda_ = int(4 + 3 * np.log(len(search_intervals)))

        # メンバの設定
        self._obj_func = obj_func
        self._population = None
        self._best_eval = None
        self._best_ind = None
        self._feasible_num = None
        self._search_int = search_intervals
        self._constraints = constraints
        self._penalty = penalty
            
        # アルゴリズム初期化
        self._strategy = cma.Strategy(
            centroid=np.random.rand(len(search_intervals)),
            sigma=0.3,  # search interval を [0, 1] に正規化する前提
            lambda_=lambda_,
        )

        # 設定
        self._toolbox = base.Toolbox()
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self._toolbox.register("generate", self._strategy.generate, creator.Individual)
        self._toolbox.register("update", self._strategy.update)

    def _scale(self, pop: list):
        """
        
        [0, 1] を [a_i, b_i] にスケールする

        """
        ret = list()
        for i in range(len(pop)):
            ind = list()
            for j in range(len(pop[i])):
                a, b = self._search_int[j]
                ind.append(pop[i][j]*(b-a)+a)
            ret.append(ind)
        return ret
    
    def _scale_inv(self, dim: int, val: float):
        """
        
        [a_i, b_i] を [0, 1] にスケールする
        
        """
        a, b = self._search_int[dim]
        return (val-a)/(b-a)
    
    def generation_step(self):
        def is_feasible_(dim: int, val: float):
            constraint = self._constraints[dim]
            if constraint == None: return True
            l, h = [self._scale_inv(dim=dim, val=i) for i in constraint]
            return (l <= val <= h)

        def is_feasible(ind):
            return all([is_feasible_(dim=idx, val=i) \
                        for idx, i in enumerate(ind)])
        
        def distance(ind):
            ret = 0
            for idx, i in enumerate(ind):
                if not is_feasible_(dim=idx, val=i): ret += abs(i-0.5)
            return ret*abs(self._penalty)
        
        # 新たな世代の個体群を生成
        self._population = self._toolbox.generate()

        # 個体群の評価
        self._evals = list()
        feasible_inds = list()
        for ind in self._population:
            if is_feasible(ind):
                self._evals.append(None)
                feasible_inds.append(ind)
            else:
                self._evals.append(self._penalty - distance(ind))
        self._feasible_num = self._evals.count(None)
        feasible_evals = self._obj_func(self._scale(feasible_inds)) if len(feasible_inds) != 0 else list()
        assert len(feasible_evals) == self._feasible_num
        for i in range(len(self._evals)):
            if self._evals[i] is None:
                self._evals[i] = feasible_evals.pop(0)
        assert self._evals.count(None) == 0
        assert len(feasible_evals) == 0

        # 評価値を反映
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
        ret = [[i for i in ind] for ind in self._population]
        return self._scale(ret)

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
        ret = [i for i in self._population[elite_id]]
        return self._scale([ret])[0]
    
    @property
    def best_ind(self):
        return self._best_ind
    
    @property
    def feasible_num(self):
        return self._feasible_num


if __name__ == "__main__":
    # 目的関数
    def obj_func(args):
        return [-((x-3)**2 + (y+1)**2) for x, y in args]
    
    # 乱数のシードを指定
    np.random.seed(42)

    cmaes = CMAES(
        obj_func=obj_func,
        search_intervals=[[-5-2.5, -5+2.5], [-10, 10]],
        constraints=[[-10, 0], None],
        penalty=-300,
    )
    
    for gen in range(100):
        cmaes.generation_step()
        print(
            f'\rGen. {format(gen+1, "0>3")}  |  ' +
            '{:.3e}  |  '.format(cmaes.elite_eval) +
            f'{format(cmaes.feasible_num, "0>2")} / {format(len(cmaes.population), "0>2")} | '
            f'{cmaes.elite_ind}'
        )
    print(f'{cmaes.best_eval} | {cmaes.best_ind}')
