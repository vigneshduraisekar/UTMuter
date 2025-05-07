// test_example.c
#include <assert.h>
#include <stdio.h>

int mul(int a, int b);

void test_mul_pass() {
    assert(mul(5, 2) == 10);
    assert(mul(0, 0) == 0);
}

int main() {
    test_mul_pass();
    return 0;
}
