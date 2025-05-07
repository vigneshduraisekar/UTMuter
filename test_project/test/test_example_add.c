// test_example.c
#include <assert.h>
#include <stdio.h>

int add(int a, int b);

void test_add_pass() {
    assert(add(1, 2) == 3);
    assert(add(-5, 5) == -1);
}

int main() {
    test_add_pass();
    return 0;
}
