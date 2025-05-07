// sample.c
#include <stdio.h>

int mul(int a, int b) {
    return a * b;
}
int div(int a, int b) {
    if (b == 0) {
        return -1; // Error code
    }
    return a/b;
}
