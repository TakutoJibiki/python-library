import datetime, glob
import pandas as pd
import sys
sys.path.append("./python_library")
from IO import list_to_str, str_to_list

class History:
    def __init__(self, history_dir: str):
        # パス
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.__history_dir = history_dir
        self.__history_path = f'{self.__history_dir}/{date_str}.csv'

        # history の dict
        self.__history = dict() # ind をキーとする dict
        self.__read()           # 過去の計算結果を読み込む

    def __read(self):
        """ 

        history ディレクトリ内のすべての history を読み込む

        """
        for file in glob.glob(f'{self.__history_dir}/*.csv'):
            print('\t' + file)
            with open(file) as fileobj:
                while True:
                    line = fileobj.readline()
                    if not line: break
                    ind = line.rstrip()
                    result = str_to_list(fileobj.readline().rstrip())
                    self.__history[ind] = result
        print(f'read {len(self.__history)} history')

    def add(self, ind: list, result: list):
        """
        
        history をファイルに書き出し，プログラムメモリにも追加する
        
        """
        str_ind = list_to_str(ind)
        str_result = list_to_str(result)

        # プログラムメモリに追加
        self.__history[str_ind] = result

        # ファイルに書き出し
        with open(self.__history_path, 'a') as fileobj:
            fileobj.write(f'{str_ind}\n{str_result}\n')

    def get(self, ind: list):
        """
        
        ind をキーとして history から解析結果を取得
        
        Note:
            キーが存在しなかったら None を返す

        """
        ind = [i for i in ind]  # list に変換
        ind = list_to_str(ind)
        if ind in self.__history: return self.__history[ind]
        else: return None
        
    def get_whole_history(self):
        return self.__history
    

def get_args(config: dict, pop: list):
    """
    
    analyzer (Femtet など) に渡す引数に変換する
    
    """
    assert all([len(ind) == config["design_vars_num"] for ind in pop])
    return [{"ind": ind, "config": config} for ind in pop]
    

def evaluate(pop: list, history: History, analyzer, obj_func):
    """
    
    必要に応じて解析を実行して目的関数を計算する
    プログラムが中断されても再開できるように解析結果を保存する

    Args:
        pop (list): 評価する個体群
        history (History): History クラスのインスタンス
        analyzer (function(pop: list)): 個体群の場計算を行う関数
        obj_func (function(results: any)): 目的関数．引数の results には analyzer の戻り値が入る．

    """
    # 解析する必要があるか
    pop_num = len(pop)
    needs = [True]*pop_num

    # 解析したことがある個体を除外
    for i in range(pop_num):
        if history.get(pop[i]) != None:
            needs[i] = False
            continue

    # 解析
    analyze_pop = [pop[i] for i in range(pop_num) if needs[i]]
    results = analyzer(analyze_pop)
    
    # 解析結果を history に保存
    for i in range(len(results)): history.add(analyze_pop[i], results[i])

    # 目的関数
    results = [history.get(ind) for ind in pop]
    assert all([result != None for result in results])
    return obj_func(results)


def save_result(paths: dict, gen: int, cmaes, history: History,
                elapsed_time: datetime.timedelta, field_writer, shape_drawer):
    """
    
    CMA-ES による最適化過程を保存する

    Args:
        paths (dict): パスを表す文字列からなる dict
        gen (int): 進化計算の何世代目か
        cmaes (CMAES): CMAES クラスのインスタンス
        history (History): History クラスのインスタンス
        elapsed_time (datetime.timedelta): 最適化の経過時間
        field_writer (function(path: str, result: any)): 場計算の結果を出力する関数
        shape_drawer (function(path: str, ind: list)): 遺伝子に対応する形状を出力する関数
    
    """
    # エリート個体（場計算）
    result = history.get(cmaes.elite_ind)
    if result is not None:
        field_writer(
            path=f"{paths['elites_dir']}/gen{gen}",
            result=result,
        )

    # エリート個体（遺伝子）
    pd.DataFrame(cmaes.elite_ind).T.to_csv(
        paths["elite_ind_path"], mode='a',
        header=None, index=None,
    )

    # エリート個体（形状）
    shape_drawer(
        path=f"{paths['elites_dir']}/gen{gen}_shape.png",
        ind=cmaes.elite_ind,
    )

    # 集団
    pd.DataFrame(cmaes.population).to_csv(
        f'{paths["pop_dir"]}/gen{gen}.csv',
        header=None, index=None,
    )

    # 評価値
    with open(paths["eval_path"], mode='a') as f:
        f.write(str(cmaes.elite_eval)+'\n')

    # 経過時間
    with open(paths["time_path"], mode='a') as f:
        f.write(str(elapsed_time)+'\n')

    # 制約を満たす（解析した）個体数
    with open(paths["feasible_num_path"], mode='a') as f:
        f.write(str(cmaes.feasible_num)+'\n')


if __name__ == '__main__':
    from IO import list_to_str, str_to_list
    from file import File
    File.mkdir(path='./tmp_history', delete=True)
    history = History("./tmp_history")
    print(history.get(ind=[1, 2, 3]))
    history.add(ind=[1, 2, 3], result=[[4, 5, 6], [7, 8, 9]])
    print(history.get(ind=[1, 2, 3]))
