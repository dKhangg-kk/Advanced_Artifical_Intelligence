"""Mã thay thế phục vụ notebook 05; không phải mã riêng của tác giả.

frontier_option: 3 = cho phép trùng, 2 = bỏ trùng, 1 = thay node trùng
và đưa node mới lên đỉnh stack. Kiểm tra chu trình trên đường đi của node.
"""
from dataclasses import dataclass

_order = 'NESW'
_moves = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}


def set_order(order='NESW'):
    global _order
    if len(order) != 4 or set(order) != set(_moves):
        raise ValueError('order phải là hoán vị của NESW')
    _order = order
    print('Thứ tự thêm vào stack:', list(order))


@dataclass(eq=False)
class Node:
    pos: tuple
    parent: object = None
    action: str = None

    def branch(self):
        nodes, node = [], self
        while node is not None:
            nodes.append(node)
            node = node.parent
        return nodes[::-1]


def DFS(maze, vis=False, animation=True, max_tries=500, frontier_option=1):
    import numpy as np
    from maze_helper import find_pos, show_maze
    if frontier_option not in (1, 2, 3):
        raise ValueError('frontier_option phải là 1, 2 hoặc 3')
    if max_tries < 1:
        raise ValueError('max_tries phải dương')
    start, goal = find_pos(maze, 'S'), find_pos(maze, 'G')
    frontier = [Node(start)]
    frames, reached = [], set()
    expanded = popped = skipped = repeats = 0
    peak = 1
    solution = None

    def snapshot(branch):
        if not animation:
            return
        frame = np.copy(maze)
        for n in frontier:
            if frame[n.pos] not in ('S', 'G'):
                frame[n.pos] = 'F'
        for n in branch:
            if frame[n.pos] not in ('S', 'G'):
                frame[n.pos] = 'P'
        frames.append(frame)

    snapshot([])
    while frontier and popped < max_tries:
        node = frontier.pop()  # LIFO: phần tử cuối được lấy trước
        popped += 1
        branch = node.branch()
        ancestors = {n.pos for n in branch[:-1]}
        if node.pos in ancestors:
            skipped += 1
            snapshot(branch[:-1])
            continue
        if node.pos == goal:
            solution = branch
            snapshot(branch)
            break
        expanded += 1
        if node.pos in reached:
            repeats += 1
        reached.add(node.pos)  # Chỉ đo lường, KHÔNG dùng để loại node
        for action in _order:
            dr, dc = _moves[action]
            pos = (node.pos[0] + dr, node.pos[1] + dc)
            if not (0 <= pos[0] < maze.shape[0] and 0 <= pos[1] < maze.shape[1]):
                continue
            if maze[pos] == 'X':
                continue
            child = Node(pos, node, action)
            duplicates = [i for i, old in enumerate(frontier) if old.pos == pos]
            if frontier_option == 2 and duplicates:
                continue
            if frontier_option == 1:
                # Dùng parent của nhánh hiện tại khi tăng ưu tiên.
                # Giữ parent cũ sẽ làm đường đi không tương ứng với lần phát hiện mới.
                for i in reversed(duplicates):
                    frontier.pop(i)
            frontier.append(child)
        peak = max(peak, len(frontier))
        snapshot(branch)
    status = ('found' if solution is not None else
              'limit' if frontier else 'exhausted')
    result = {
        'path': None if solution is None else [n.pos for n in solution],
        'actions': None if solution is None else [n.action for n in solution[1:]],
        'reached': reached, 'maze_anim': frames,
        'status': status, 'popped': popped, 'expanded': expanded,
        'skipped_cycles': skipped, 'repeated_expansions': repeats,
        'peak_frontier': peak, 'remaining_frontier': len(frontier),
    }
    if vis:
        show_maze(frames[-1] if frames else maze)
    return result


def animate_maze(result):
    """Trả về HTML để animation hiển thị trong notebook và bản xuất HTML."""
    from IPython.display import HTML
    from maze_helper import animate_maze as helper_animation
    if not result['maze_anim']:
        raise ValueError('Cần chạy DFS với animation=True')
    if result['status'] == 'limit':
        print('Dừng do đạt max_tries; chưa thể kết luận mê cung vô nghiệm.')
    ani = helper_animation(result)
    return HTML(ani.to_jshtml())
