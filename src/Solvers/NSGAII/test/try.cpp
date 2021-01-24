#include <memory>
#include <iostream>
#include <vector>
#include <assert.h>
#include <random>
#include <limits>
#include <functional>
#include <algorithm>

using namespace std;

class A {
public:
    vector<int> b;
};

vector<int> random_vector(int size) {
    std::random_device rd;
    std::mt19937 mt(rd());
    std::uniform_int_distribution<int> dist(1, 9);
    vector<int> tmp(size);
    for (int i = 0; i < size; ++ i) {
        tmp.at(i) = dist(mt);
    }
    return tmp;
}

int main(){
    cout << ((numeric_limits<double>::max()) == (numeric_limits<double>::max())) << endl;
    return 0;
}