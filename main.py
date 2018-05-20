import sys

GRID_HEIGHT = 10
GRID_WIDTH = 10

X_SECTORS = 2
Y_SECTORS = 2

BLOCKED = "*"
FILLED = "+"
UNFILLED = "."
POSSIBLE = "o"

NORTH = 1
SOUTH = 2
WEST = 3
EAST = 4
SURFACE = 5

def init_grid():
    grid = []
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            grid.append(UNFILLED)
    return grid

def print_grid(grid):
    print("   ", end='')
    for i in range(GRID_WIDTH):
        if (i % int(GRID_WIDTH / X_SECTORS)) == 0:
            print("  ", end='')
        print("{} ".format(chr(i + 97).upper()), end='')
    print()

    for i in range(GRID_HEIGHT):

        if (i % int(GRID_HEIGHT / Y_SECTORS)) == 0:
            print('   ', end='')
            for j in range(GRID_WIDTH):
                if (j % int(GRID_HEIGHT / Y_SECTORS)) == 0:
                    print('  ', end='')
                print('- ', end='')
            print()

        print("{:>2} ".format(i + 1), end='')
        for j in range(GRID_WIDTH + 1):
            if j == GRID_WIDTH:
                print('|')
                break

            if (j % int(GRID_HEIGHT / Y_SECTORS)) == 0:
                print("| ", end='')

            idx = i * GRID_WIDTH + j
            print("{} ".format(grid[idx]), end='')

    print('   ', end='')
    for j in range(GRID_WIDTH):
        if (j % int(GRID_HEIGHT / Y_SECTORS)) == 0:
            print('  ', end='')
        print('- ', end='')
    print()

def map_valid_starts(grid, valid_starts):
    for idx in valid_starts:
        grid[idx] = POSSIBLE

# Generates grid appropriate index from human readable index
def g_idx(idx_str):
    tmp_str = idx_str.lower()
    x = ord(tmp_str[0]) - 97
    y = int(tmp_str[1:]) - 1

    idx = y * GRID_WIDTH + x
    return idx

# Generates human readable index from grid appropriate index
def v_idx(idx):
    x = int(idx / GRID_WIDTH)
    y = int(idx % GRID_WIDTH) + 1
    idx_str = "{}{}".format(chr(x + 97).upper(), y)

    return idx_str

def is_open_space(grid, idx):
    if grid[idx] == FILLED or grid[idx] == BLOCKED:
        return False
    return True

def is_valid_space(grid, x, y):
    idx = y * GRID_WIDTH + x

    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT or \
            not is_open_space(grid, idx):
        return False

    return True

def move(grid, ship_idx, direction):
    ship_x = int(ship_idx % GRID_WIDTH)
    ship_y = int(ship_idx / GRID_WIDTH)

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

    if not is_valid_space(grid, new_x, new_y):
        return -1

    # print("({},{}) -> ({},{})".format(ship_x, ship_y, new_x, new_y))

    new_idx = new_y * GRID_WIDTH + new_x

    return new_idx

def valid_path(grid, start, moves):
    tmp_grids = []
    tmp_grids.append(grid[:])
    tmp_grid = tmp_grids[-1]

    cur_idx = start
    tmp_grid[cur_idx] = FILLED

    for move_dir in moves:
        if move_dir == SURFACE:
            tmp_grids.append(grid[:])
            tmp_grid = tmp_grids[-1]

        new_idx = move(tmp_grid, cur_idx, move_dir)
        if new_idx == -1:
            return False

        cur_idx = new_idx
        tmp_grid[cur_idx] = FILLED

    print("----------------------")
    for idx, tgrid in enumerate(tmp_grids):
        print_grid(tgrid)

        if idx != len(tmp_grids) - 1:
            print()
    print("----------------------\n")

    return True

def print_move_history(move_history):
    for move in move_history:
        if move == NORTH:
            print("NORTH ", end='')
        elif move == SOUTH:
            print("SOUTH ", end='')
        elif move == WEST:
            print("WEST ", end='')
        elif move == EAST:
            print("EAST ", end='')
        elif move == SURFACE:
            print("EAST ", end='')
    print()

def parse_historyfile(filename):
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
            move_history.append(NORTH)
        elif command == "S":
            move_history.append(SOUTH)
        elif command == "W":
            move_history.append(WEST)
        elif command == "E":
            move_history.append(EAST)
        elif command == "SU":
            move_history.append(SURFACE)

    return (ship_pos, move_history)

def parse_mapfile(filename):
    map_txt = ""
    with open(filename, "r") as f:
        map_txt = f.read()

    grid = init_grid()
    positions = map_txt.splitlines()
    for position in positions:
        grid[g_idx(position)] = BLOCKED

    return grid

if len(sys.argv) != 3:
    print("Expects {} <map file> <history file>".format(sys.argv[0]))
    sys.exit(1)

mapfile_name = sys.argv[1]
historyfile_name = sys.argv[2]

grid = parse_mapfile(mapfile_name)
(ship_pos, move_history) = parse_historyfile(historyfile_name)

print("Printing all possible move sets\n")
valid_starts = []
for start_idx in range(GRID_WIDTH * GRID_HEIGHT):
    if is_open_space(grid, start_idx):
        if valid_path(grid, start_idx, move_history):
            valid_starts.append(start_idx)

print("Printing all valid potential starting points\n")
i = 1
for idx in valid_starts:
    print("{}, ".format(v_idx(idx)), end='')
    if (i % 5) == 0:
        print("")
    i += 1
print("\n")

print("Graphing all valid potential starting points\n")
map_valid_starts(grid, valid_starts)
print_grid(grid)
