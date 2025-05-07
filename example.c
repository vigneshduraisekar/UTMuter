// example.c
#include <stdio.h>

int add(int a, int b) {
    if(a < 0 || b < 0) {
        return -1; // Error code
    }
    return a + b;
}
int sub(int a, int b) {
    return a - b;
}
