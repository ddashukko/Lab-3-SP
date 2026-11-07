// Демо: факторіал, Фібоначчі, прості числа, dangling else
int counter = 0;

int fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}

int fib(int n) {
    int a = 0;
    int b = 1;
    for (int i = 0; i < n; i = i + 1) {
        int t = a + b;
        a = b;
        b = t;
    }
    return a;
}

int is_prime(int n) {
    if (n < 2) return 0;
    int d = 2;
    while (d * d <= n) {
        if (n % d == 0) return 0;
        d = d + 1;
    }
    return 1;
}

float average(int a, int b) {
    return (a + b) / 2.0;
}

int main() {
    print("fact(6) =", fact(6));
    print("fib(10) =", fib(10));
    for (int k = 1; k <= 20; k = k + 1) {
        if (is_prime(k)) { print("prime:", k); counter = counter + 1; }
    }
    print("primes found:", counter);
    print("avg =", average(3, 4));
    print("-7 / 2 =", -7 / 2, " -7 % 3 =", -7 % 3);
    int x = 5;
    if (x > 3) if (x > 10) print("big"); else print("medium"); // else -> до внутрішнього if
    return 0;
}
