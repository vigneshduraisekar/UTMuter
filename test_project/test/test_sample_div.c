// test_example.c
#include <assert.h>
#include <stdio.h>

int div(int a, int b);

void test_div_pass() {
    assert(div(6, 3) == 2);
    assert(div(0, 0) == -1);
}

int main() {
    test_div_pass();
    return 0;
}
