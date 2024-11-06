#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <cassert>
#include <queue>
#include <execution>
#include "stdout.hpp"
#include "algorithm.hpp" /* TODO:cxx-libraryの コミットID */

using std::cout, std::endl;
using int2 = std::pair<int, int>;
using Mat = std::vector<std::vector<int>>;

const std::vector<int> DI{0, 1, 0, -1};
const std::vector<int> DJ{1, 0, -1, 0};
constexpr int ON = 255;
constexpr int OFF = 0;

void flood_fill(Mat &arr, const int begin_y, const int begin_x, const int r_color, const int direction)
{
    assert(direction == 4 or direction == 8);
    int t_color = arr[begin_y][begin_x];
    if (t_color == r_color)
        return;
    std::queue<int2> q;
    q.push({begin_y, begin_x});
    arr[begin_y][begin_x] = r_color;

    std::vector<int> DX = {1, 0, -1, 0, 1, -1, -1, 1};
    std::vector<int> DY = {0, 1, 0, -1, 1, 1, -1, -1};

    while (!q.empty())
    {
        auto [y, x] = q.front();
        q.pop();
        for (int i = 0; i < direction; ++i)
        {
            int nx = x + DX[i];
            int ny = y + DY[i];
            if (!(0 <= nx and nx < arr[0].size()))
                continue;
            if (!(0 <= ny and ny < arr.size()))
                continue;
            if (arr[ny][nx] == t_color)
            {
                arr[ny][nx] = r_color;
                q.push({ny, nx});
            }
        }
    }
}

/* 入力された二値画像のうち，指定された座標 (begin) を含む領域の境界を抽出する */
std::vector<int2> extract_boundary(const Mat &img, const int2 begin)
{
    const int H = img.size();
    const int W = img[0].size();

    /* 境界を抽出 */
    std::vector<int2> boundary{begin};
    int search_cnt = 0;
    while (true)
    {
        auto [i, j] = boundary.back();
        for (int k = 0; k < 4; ++k)
        {
            int ni = i + DI[(search_cnt + k) % 4];
            int nj = j + DJ[(search_cnt + k) % 4];
            if (!(0 <= ni and ni < H))
                continue;
            if (!(0 <= nj and nj < W))
                continue;
            if (img[ni][nj] != img[begin.first][begin.second])
                continue;
            boundary.emplace_back(ni, nj);
            search_cnt = (search_cnt + k - 1 + 4) % 4; /* % で割られる値が負になると期待通りに動作しない */
            break;
        }

        if (boundary.size() > 1 and boundary.front() == boundary.back())
            break;
    }

    /* 境界から頂点を抽出する */
    std::vector<int2> vertices{boundary.front()};
    for (int k = 1; k < boundary.size() - 1; ++k)
    {
        auto [i1, j1] = boundary[k - 1];
        auto [i2, j2] = boundary[k];
        auto [i3, j3] = boundary[k + 1];
        if (i1 == i2 and i2 == i3)
            continue;
        if (j1 == j2 and j2 == j3)
            continue;
        vertices.emplace_back(boundary[k]);
    }
    return vertices;
}

/* 入力された二値画像の境界を抽出する */
std::vector<std::vector<int2>> extract_boundaries(const Mat &img)
{
    const int H = img.size();
    const int W = img[0].size();
    auto to = [W](int i, int j)
    { return i * W + j; };
    auto to_ = [W](int x)
    { return int2{int(x / W), x % W}; };

    /* ４近傍で同じ色の画素をグループにまとめる */
    UnionFind uf(H * W);
    for (int i = 0; i < H; ++i)
    {
        for (int j = 0; j < W; ++j)
        {
            for (int k = 0; k < 4; ++k)
            {
                int ni = i + DI[k];
                int nj = j + DJ[k];
                if (!(0 <= ni and ni < H))
                    continue;
                if (!(0 <= nj and nj < W))
                    continue;
                if (img[i][j] != img[ni][nj])
                    continue;
                uf.merge(to(i, j), to(ni, nj));
            }
        }
    }

    /* 各グループを代表するインデックスを取得 */
    std::vector<int2> begins;
    for (auto [k, v] : uf.get_all_group_members())
    {
        /* 各グループの最小のインデックス */
        auto [min_i, min_j] = to_(*std::min_element(v.begin(), v.end()));
        if (img[min_i][min_j] == ON)
            begins.emplace_back(min_i, min_j);
    }

    /* 境界の節点を抽出 */
    std::vector<std::vector<int2>> boundaries(begins.size());
    for (int i = 0; i < boundaries.size(); ++i)
        boundaries[i] = extract_boundary(img, begins[i]);
    return boundaries;
}

std::vector<std::vector<std::vector<int2>>> decompose(const Mat &img)
{
    /* 画像形式の二次元配列か確認 */
    const int H = img.size();
    const int W = img[0].size();
    for (const auto i : img)
        assert(i.size() == W);

    /* 二値画像か確認 */
    for (const auto &vec : img)
        for (const auto i : vec)
            assert(i == OFF or i == ON and "img must be binary");

    /* 画像を二倍に拡大して外周を追加 */
    Mat enlarged_img(H * 2 + 2, std::vector<int>(W * 2 + 2, ON));
    for (int i = 0; i < H; ++i)
        for (int j = 0; j < W; ++j)
            for (int k = 0; k < 2; ++k)
                for (int l = 0; l < 2; ++l)
                    enlarged_img[1 + i * 2 + k][1 + j * 2 + l] = img[i][j];

    /* 交互に塗りつぶしながら境界を抽出 */
    std::vector<std::vector<std::vector<int2>>> geometry;
    int cnt = 0;
    while (true)
    {
        auto tmp = enlarged_img;
        flood_fill(tmp, 0, 0, (cnt % 2 == 0) ? OFF : ON, 4);

        /* flood fill の前後で変わらなかった部分を抽出 */
        Mat diff(tmp.size(), std::vector<int>(tmp[0].size()));
        for (int i = 0; i < tmp.size(); ++i)
            for (int j = 0; j < tmp[0].size(); ++j)
                diff[i][j] = 255 - abs(tmp[i][j] - enlarged_img[i][j]);

        enlarged_img = std::move(tmp);
        cnt += 1;

        /* 一切変化しなかったら終了 */
        auto is_all_zero = [](const Mat &mat)
        {
            for (int i = 0; i < mat.size(); ++i)
                for (int j = 0; j < mat[0].size(); ++j)
                    if (mat[i][j] != 0)
                        return false;
            return true;
        };
        if (is_all_zero(diff))
            break;

        /* 境界を抽出 */
        geometry.emplace_back(extract_boundaries(diff));
    }

    return geometry;
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
    auto geometry = decompose(img);
    cout << geometry << endl;

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
