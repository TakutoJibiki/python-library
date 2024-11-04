#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <cassert>
#include "stdout.hpp"

using std::cout, std::endl;
using int2 = std::pair<int, int>;
using Mat = std::vector<std::vector<int>>;

void decompose(const Mat &img, std::vector<std::vector<std::vector<int2>>> &geometry)
{
    const int H = img.size();
    const int W = img[0].size();

    /* 画像形式の二次元配列か確認 */
    for (const auto i : img)
        assert(i.size() == W);

    /* 二値画像か確認 */
    for (const auto &vec : img)
        for (const auto i : vec)
            assert(i == 0 or i == 255 and "img must be binary");

    /* 画像を二倍に拡大 */
    Mat enlarged_img(H * 2, std::vector<int>(W * 2));
    for (int i = 0; i < H; ++i)
        for (int j = 0; j < W; ++j)
            for (int k = 0; k < 2; ++k)
                for (int l = 0; l < 2; ++l)
                    enlarged_img[i * 2 + k][j * 2 + l] = img[i][j];
}

int main(void)
{
    const std::string IN_PATH = "./in";
    const std::string OUT_PATH = "./out";

    /* 入力読み込み */
    std::ifstream ifs_in(IN_PATH);
    int H, W;
    ifs_in >> H >> W;
    Mat img(H, std::vector<int>(W));
    for (int i = 0; i < H; ++i)
        for (int j = 0; j < W; ++j)
            ifs_in >> img[i][j];

    /* polygon_decomposer */
    std::vector<std::vector<std::vector<int2>>> geometry;
    decompose(img, geometry);

    /* 出力読み込み */
    // std::vector<std::vector<std::vector<int2>>> geometry;
    // {
    //     std::ifstream ifs_out(OUT_PATH);
    //     int N;
    //     ifs_out >> N;
    //     for (int i = 0; i < N; ++i)
    //     {
    //         int M;
    //         ifs_out >> M;
    //         std::vector<int> mm(M);
    //         for (auto &j : mm)
    //             ifs_out >> j;
    //         std::vector<std::vector<int2>> polygons;
    //         for (auto j : mm)
    //         {
    //             std::vector<int2> polygon(j);
    //             for (auto &[y, x] : polygon)
    //                 ifs_out >> y >> x;
    //             polygons.emplace_back(polygon);
    //         }
    //         geometry.emplace_back(polygons);
    //     }
    // }
    // cout << geometry << endl;

    return 0;
}
