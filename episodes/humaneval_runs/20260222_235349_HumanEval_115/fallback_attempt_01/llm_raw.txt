def max_fill(grid, capacity):
    total_water_units = sum(sum(row) for row in grid)
    return (total_water_units + capacity - 1) // capacity