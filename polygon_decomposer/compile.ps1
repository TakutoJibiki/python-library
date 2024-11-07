# cxx-library のバージョンは cxx_decompose.cpp の上部を参照
g++ cxx_decompose.cpp `
    -I ./../../cxx-library/source `
    -std=c++17 -o cxx_decompose.exe
