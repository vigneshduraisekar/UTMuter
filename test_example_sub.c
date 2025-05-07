// test_example.c
#include <assert.h>
#include <stdio.h>

int sub(int a, int b);

void test_sub_pass() {
    assert(sub(5, 3) == 2);
    assert(sub(0, 0) == 0);
}

int main() {
    test_sub_pass();
    return 0;
}
