import sys

BLOCKED = "*"
FILLED = "+"
UNFILLED = "."
POSSIBLE = "o"

NORTH = 1
SOUTH = 2
WEST = 3
EAST = 4
SURFACE = 5
SILENCE = 6
DRONE = 7

def to_coords(width, idx):
    return (int(idx % width), int(idx / width))

def to_idx(width, x, y):
    return y * width + x

def init_grid(width, height):
    grid = []
    for i in range(width):
        for j in range(height):
            grid.append(UNFILLED)
    return grid

def print_grid(grid, width, height, x_sectors, y_sectors):

    # generate top headers (A -> J)
    print("   ", end='')
    for i in range(width):
        if (i % int(width / x_sectors)) == 0:
            print("  ", end='')
        print("{} ".format(chr(i + 97).upper()), end='')
    print()

    # Fill with number, spacer, row data, and end spacer
    for i in range(height):
        if (i % int(height / y_sectors)) == 0:
            print('   ', end='')
            for j in range(width):
                if (j % int(height / y_sectors)) == 0:
                    print('  ', end='')
                print('- ', end='')
            print()

        print("{:>2} ".format(i + 1), end='')
        for j in range(width + 1):
            if j == width:
                print('|')
                break

            if (j % int(height / y_sectors)) == 0:
                print("| ", end='')

            idx = i * width + j
            print("{} ".format(grid[idx]), end='')

    # generate end cap
    print('   ', end='')
    for j in range(width):
        if (j % int(height / y_sectors)) == 0:
            print('  ', end='')
        print('- ', end='')
    print()

def map_possible_points(grid, possible_points):
    for idx in possible_points:
        grid[idx] = POSSIBLE

# Generates grid appropriate index from human readable index (A1 -> 0)
def g_idx(width, idx_str):
    tmp_str = idx_str.lower()
    x = ord(tmp_str[0]) - 97
    y = int(tmp_str[1:]) - 1

    idx = y * width + x
    return idx

# Generates human readable index from grid appropriate index (0 -> A1)
def v_idx(width, idx):
    (x, y) = to_coords(width, idx)
    idx_str = "{}{}".format(chr(x + 97).upper(), y + 1)

    return idx_str

def is_open_space(grid, idx):
    if grid[idx] == FILLED or grid[idx] == BLOCKED:
        return False
    return True

def is_valid_space(grid, width, height, x, y):
    idx = y * width + x

    if x < 0 or x >= width or y < 0 or y >= height or \
            not is_open_space(grid, idx):
        return False

    return True

# assumes minimum stays the same (0)
def rerange(value, old_max, new_max):
    return int((value * new_max) / old_max)

# turns grid flat idx into sector flat idx
# for grid 4x4 with 2x2 sectors: grid(9) => grid(1, 2) -> sector(1, 0) => sector(2)
def grid_idx_to_sector_idx(idx, width, height, x_sectors, y_sectors):
    x = int(idx % width)
    y = int(idx / width)

    sect_x = rerange(x, width, x_sectors)
    sect_y = rerange(y, height, y_sectors)

    sect_idx = sect_y * x_sectors + sect_x
    return sect_idx

def move(grid, width, height, ship_idx, direction):
    (ship_x, ship_y) = to_coords(width, ship_idx)

    new_x = ship_x
    new_y = ship_y

    if direction == NORTH:
        new_y -= 1
    elif direction == SOUTH:
        new_y += 1
    elif direction == WEST:
        new_x -= 1
    elif direction == EAST:
        new_x += 1

    if not is_valid_space(grid, width, height, new_x, new_y):
        return -1

    # print("({},{}) -> ({},{})".format(ship_x, ship_y, new_x, new_y))

    new_idx = to_idx(width, new_x, new_y)

    return new_idx

def get_active_leaves(grid_tree):
    if grid_tree.failed:
        return []

    grid_leaves = []
    if len(grid_tree.children) == 0:
        grid_leaves += [grid_tree]
    else:
        for child in grid_tree.children:
            grid_leaves += get_active_leaves(child)

    return grid_leaves

def get_all_leaves(grid_tree):
    grid_leaves = [grid_tree]

    for child in grid_tree.children:
        grid_leaves += get_active_leaves(child)

    return grid_leaves



class GridNode:
    def __init__(self):
        self.grid = []
        self.cur_idx = -1
        self.children = []
        self.failed = False

def build_grid_tree(grid, width, height, x_sectors, y_sectors, start, moves):
    grid_tree = GridNode()
    grid_tree.grid = grid[:]
    grid_tree.start_idx = start
    grid_tree.cur_idx = start
    grid_tree.grid[grid_tree.cur_idx] = FILLED

    for (move_dir, extra) in moves:
        grid_nodes = get_active_leaves(grid_tree)
        if move_dir == SURFACE:
            for grid_node in grid_nodes:

                sector_idx = grid_idx_to_sector_idx(grid_node.cur_idx, width, height, x_sectors, y_sectors)
                if extra == sector_idx:
                    new_grid = GridNode()
                    new_grid.grid = grid[:]
                    new_grid.start_idx = start
                    new_grid.cur_idx = grid_node.cur_idx
                    grid_node.children.append(new_grid)
                else:
                    grid_node.failed = True

        elif move_dir == DRONE:
            for grid_node in grid_nodes:

                sector_idx = grid_idx_to_sector_idx(grid_node.cur_idx, width, height, x_sectors, y_sectors)
                if sector_idx in extra:
                    new_grid = GridNode()
                    new_grid.grid = grid[:]
                    new_grid.start_idx = start
                    new_grid.cur_idx = grid_node.cur_idx
                    grid_node.children.append(new_grid)
                else:
                    grid_node.failed = True

        elif move_dir == SILENCE:
            for grid_node in grid_nodes:
                tmp_grid = grid_node.grid

                path_options = []

                cur_idx = grid_node.cur_idx
                n_idx = cur_idx
                s_idx = cur_idx
                w_idx = cur_idx
                e_idx = cur_idx

                for i in range(0, 4):
                    if n_idx != -1:
                        n_idx = move(tmp_grid, width, height, n_idx, NORTH)
                        if n_idx != -1:
                            path_options.append(n_idx)

                    if s_idx != -1:
                        s_idx = move(tmp_grid, width, height, s_idx, SOUTH)
                        if s_idx != -1:
                            path_options.append(s_idx)

                    if w_idx != -1:
                        w_idx = move(tmp_grid, width, height, w_idx, WEST)
                        if w_idx != -1:
                            path_options.append(w_idx)

                    if e_idx != -1:
                        e_idx = move(tmp_grid, width, height, e_idx, EAST)
                        if e_idx != -1:
                            path_options.append(e_idx)

                path_options.append(cur_idx)

                new_branches = len(path_options)

                (cur_x, cur_y) = to_coords(width, cur_idx)

                for branch_idx in path_options:
                    new_grid = tmp_grid[:]

                    (branch_x, branch_y) = to_coords(width, branch_idx)

                    dist_y = branch_y - cur_y
                    dist_x = branch_x - cur_x

                    horiz = False
                    if abs(dist_x) > abs(dist_y):
                        horiz = True

                    if horiz:
                        x1 = cur_x
                        x2 = branch_x
                        if x1 > x2:
                            x1, x2 = x2, x1

                        for x in range(x1, x2):
                            new_grid[to_idx(width, x, cur_y)] = FILLED
                    else:
                        y1 = cur_y
                        y2 = branch_y
                        if y1 > y2:
                            y1, y2 = y2, y1

                        for y in range(y1, y2):
                            new_grid[to_idx(width, cur_x, y)] = FILLED

                    new_grid[branch_idx] = FILLED
                    new_grid[cur_idx] = FILLED

                    new_node = GridNode()
                    new_node.start_idx = start
                    new_node.grid = new_grid
                    new_node.cur_idx = branch_idx
                    grid_node.children.append(new_node)

                    # print_grid(new_node.grid, width, height, x_sectors, y_sectors)

                opt_grid = grid[:]
                map_possible_points(opt_grid, path_options)

                opt_grid[cur_idx] = FILLED
                # print("== showing possible silence routes ==")
                # print_grid(opt_grid, width, height, x_sectors, y_sectors)
                # print("=====================================")
        else:
            for grid_node in grid_nodes:
                tmp_grid = grid_node.grid
                cur_idx = grid_node.cur_idx

                new_idx = move(tmp_grid, width, height, cur_idx, move_dir)
                if new_idx == -1:
                    grid_node.failed = True
                    continue

                cur_idx = new_idx
                tmp_grid[cur_idx] = FILLED
                grid_node.cur_idx = cur_idx

    return grid_tree

def print_move_history(move_history):
    for (move, extra) in move_history:
        if move == NORTH:
            print("NORTH ", end='')
        elif move == SOUTH:
            print("SOUTH ", end='')
        elif move == WEST:
            print("WEST ", end='')
        elif move == EAST:
            print("EAST ", end='')
        elif move == SURFACE:
            print("SURFACE ", extra, end='')
        elif move == SILENCE:
            print("SILENCE ", end='')
        elif move == DRONE:
            print("DRONE ", extra, end='')
    print()

def parse_historyfile(filename, x_sectors, y_sectors):
    history_txt = ""
    with open(filename, "r") as f:
        history_txt = f.read()

    ship_pos = None

    start_idx = 0
    commands = history_txt.splitlines()
    if commands[0].upper().startswith("POS:"):
        start_idx += 1
        ship_pos = commands[0][4:].strip()

    move_history = []
    for command in commands[start_idx:]:
        if command == "N":
            move_history.append((NORTH, 0))
        elif command == "S":
            move_history.append((SOUTH, 0))
        elif command == "W":
            move_history.append((WEST, 0))
        elif command == "E":
            move_history.append((EAST, 0))
        elif command == "SI":
            move_history.append((SILENCE, 0))
        else:
            pieces = command.split()
            if len(pieces) <= 1:
                sys.exit(1)

            if pieces[0] == "SU":
                if len(pieces) != 2:
                    print("Invalid surface args; Expected <sector>")
                    sys.exit(1)

                try:
                    sector = int(pieces[1])
                except ValueError:
                    print("Surface sector is not an integer")
                    sys.exit(1)

                max_sector = x_sectors * y_sectors
                if sector > max_sector or sector < 1:
                    print("Surface has an invalid sector")
                    sys.exit(1)

                internal_sector = sector - 1

                move_history.append((SURFACE, internal_sector))
            elif pieces[0] == "DR":
                if len(pieces) != 3:
                    print("Invalid drone args; Expected <sector> <Y/N>")
                    sys.exit(1)

                try:
                    sector = int(pieces[1])
                except ValueError:
                    print("Surface sector is not an integer")
                    sys.exit(1)

                max_sector = x_sectors * y_sectors
                if sector > max_sector or sector < 1:
                    print("Surface has an invalid sector")
                    sys.exit(1)

                internal_sector = sector - 1

                # Make a list of all sectors the sub could be in
                # If we got a Y, the list is just the passed sector
                # otherwise, it's everything but the passed sector
                rem_sectors = []
                if pieces[2] == "Y":
                    rem_sectors.append(internal_sector)
                else:
                    for i in range(0, max_sector):
                        if i != internal_sector:
                            rem_sectors.append(i)

                move_history.append((DRONE, rem_sectors))
            else:
                print("Surface move should have a defined integer sector")
                sys.exit(1)

    return (ship_pos, move_history)

def parse_mapfile(filename):
    map_txt = ""
    with open(filename, "r") as f:
        map_txt = f.read()

    lines = map_txt.splitlines()

    if len(lines) < 4:
        print("Mapfile is invalid, must contain a grid size header!")
        sys.exit(1)

    try:
        grid_height = int(lines[0])
        grid_width  = int(lines[1])
        x_sectors   = int(lines[2])
        y_sectors   = int(lines[3])
    except ValueError:
        print("Mapfile grid header is invalid! Header info should be integers")
        sys.exit(1)

    grid = init_grid(grid_width, grid_height)

    positions = lines[4:]
    for position in positions:
        grid[g_idx(grid_width, position)] = BLOCKED

    return grid, grid_height, grid_width, x_sectors, y_sectors

if len(sys.argv) != 3:
    print("Expects {} <map file> <history file>".format(sys.argv[0]))
    sys.exit(1)

mapfile_name = sys.argv[1]
historyfile_name = sys.argv[2]

grid, grid_width, grid_height, x_sectors, y_sectors = parse_mapfile(mapfile_name)
(ship_pos, move_history) = parse_historyfile(historyfile_name, x_sectors, y_sectors)

print("Printing all possible move sets\n")
valid_starts = []
valid_ends = []
for start_idx in range(grid_width * grid_height):
    if is_open_space(grid, start_idx):
        grid_tree = build_grid_tree(grid, grid_width, grid_height, x_sectors, y_sectors, start_idx, move_history)

        grid_nodes = get_active_leaves(grid_tree)
        for grid_node in grid_nodes:
            valid_ends.append(grid_node.cur_idx)
            valid_starts.append(grid_node.start_idx)

valid_starts = set(valid_starts)
valid_ends = set(valid_ends)

'''
print("Printing all valid potential starting points\n")
i = 1
for idx in valid_starts:
    print("{}, ".format(v_idx(grid_width, idx)), end='')
    if (i % 5) == 0:
        print("")
    i += 1
print("\n")
'''

print("Graphing all valid potential starting points\n")
tmp_grid = grid[:]
map_possible_points(tmp_grid, valid_starts)
print_grid(tmp_grid, grid_width, grid_height, x_sectors, y_sectors)

'''
print("Printing all valid potential current points\n")
i = 1
for idx in valid_ends:
    print("{}, ".format(v_idx(grid_width, idx)), end='')
    if (i % 5) == 0:
        print("")
    i += 1
print("\n")
'''

print("Graphing all valid potential current points\n")
tmp_grid = grid[:]
map_possible_points(tmp_grid, valid_ends)
print_grid(tmp_grid, grid_width, grid_height, x_sectors, y_sectors)
