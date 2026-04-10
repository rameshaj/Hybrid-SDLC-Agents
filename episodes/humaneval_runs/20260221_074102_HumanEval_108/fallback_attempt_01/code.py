def count_nums(arr):
    def sum_of_digits(n):
        return sum(int(d) for d in str(n) if d.isdigit()) - (int(str(n)[0]) if str(n)[0] == '-' else 0)

    return sum(1 for num in arr if sum_of_digits(num) > 0)