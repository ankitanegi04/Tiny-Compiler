int main() {
    int sum = 0;
    int i;
    for (i = 1; i <= 10; i = i + 1) {
        if (i % 2 == 0) {
            continue; 
        }
        if (i > 7) {
            break; 
        }
        sum = sum + i;
    }
    return sum; 
}