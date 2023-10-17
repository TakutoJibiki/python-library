from sklearn.decomposition import PCA

def pca(data_table):
    # 主成分分析を実行
    pca = PCA()
    feature = pca.fit(data_table)

    # データを主成分空間に写像
    feature = pca.transform(data_table)

    # print('*** 寄与率 ***')
    # print(pca.explained_variance_ratio_)

    # 寄与率，寄与率の高い２次元のデータ
    return pca.explained_variance_ratio_, [feature[:, 0].tolist(), feature[:, 1].tolist()]

if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv('dataset.csv')
    accum, compressed = pca(df)
    plt.scatter(compressed[0], compressed[1])
    plt.show()
