def minPath(grid, k):
    def dfs(x, y, path, visited):
        if len(path) == k:
            return path
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx, ny) not in visited:
                visited.add((nx, ny))
                result = dfs(nx, ny, path + [grid[nx][ny]], visited)
                if result:
                    return result
                visited.remove((nx, ny))
        return None

    min_path = None
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            visited = {(i, j)}
            result = dfs(i, j, [grid[i][j]], visited)
            if result and (min_path is None or len(result) < len(min_path)):
                min_path = result
    return min_path