def minPath(grid, k):
    def dfs(x, y, path, visited):
        if len(path) == k:
            return path
        for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in visited:
                visited.add((nx, ny))
                result = dfs(nx, ny, path + [grid[nx][ny]], visited)
                if result:
                    return result
                visited.remove((nx, ny))
        return None

    N = len(grid)
    min_path = []
    for i in range(N):
        for j in range(N):
            visited = {(i, j)}
            path = [grid[i][j]]
            result = dfs(i, j, path, visited)
            if result and (not min_path or result < min_path):
                min_path = result
    return min_path