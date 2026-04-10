def max_fill(grid, capacity):
    return sum(sum(row) // capacity for row in grid)