#include <vector>
#include <iostream>
#include <fstream>
#include "stdout.hpp"

using std::cout, std::endl;
using int2 = std::pair<int, int>;

int main(void)
{
    const std::string IN_PATH = "./in";
    const std::string OUT_PATH = "./out";

    /* 入力読み込み */
    std::ifstream ifs_in(IN_PATH);
    int H, W;
    ifs_in >> H >> W;
    std::vector<std::vector<int>> img(H, std::vector<int>(W));
    for (int i = 0; i < H; ++i)
        for (int j = 0; j < W; ++j)
            ifs_in >> img[i][j];

    /* 出力読み込み */
    std::vector<std::vector<std::vector<int2>>> geometry;
    {
        std::ifstream ifs_out(OUT_PATH);
        int N;
        ifs_out >> N;
        for (int i = 0; i < N; ++i)
        {
            int M;
            ifs_out >> M;
            std::vector<int> mm(M);
            for (auto &j : mm)
                ifs_out >> j;
            std::vector<std::vector<int2>> polygons;
            for (auto j : mm)
            {
                std::vector<int2> polygon(j);
                for (auto &[y, x] : polygon)
                    ifs_out >> y >> x;
                polygons.emplace_back(polygon);
            }
            geometry.emplace_back(polygons);
        }
    }
    cout << geometry << endl;

    return 0;
}
