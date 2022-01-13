# subnar
Tool for analysis of Captain Sonar game board state space

subnar ingests the game map and shorthand for moves from each side, 
and then spits out every possible location for subs.

Alpha, Beta, and Zeta maps are included for solution paring.

## Ship History Format:
N, S, W, E -- Announced Heading (Head: North, South, West, East)
SI -- Activate Silence (limits the movement/direction space to linear paths of limited distance)
SU -- Surface (announces current sector of submarine in game, subnar doesn't currently ingest sector info)

## Result Graph Format:
o -- Possible sub piece location
+ -- Known sub piece location
. -- Known empty location
* -- Location blocked by terrain (sub can't be here)

## Example
Ship History:
```
N
N
N
N
W
W
SI
SU
```

Final Solution Space:
```
=====================================
Printing all valid potential starting points

F7, I10, J10, I7, J7,
F8, G5, I5, J5, C9,
D6, F9, F6, G6, J9,
I9, C10, D7,

Graphing all valid potential starting points

     A B C D E F G H I J
     - - - - - - - - - -
 1 | . . . * . . . . . . |
 2 | . . . . . . . * . . |
 3 | . . . . . . . . . . |
 4 | . . * . . . . * . . |
 5 | . . . . . . o . o o |
 6 | . . . o * o o . . . |
 7 | . . . o . o * . o o |
 8 | . . . . . o . . . . |
 9 | . . o * . o . * o o |
10 | . . o . . . . . o o |
     - - - - - - - - - -
Printing all valid potential current points

A1, B1, E1, F1, G1,
H1, A2, B2, C2, D2,
E2, G2, A3, B3, C3,
D3, E3, F3, G3, H3,
A4, B4, D4, E4, G4,
A5, B5, C5, D5, E5,
F5, G5, H5, A6, B6,
D6, F6, G6, H6, A7,
B7, D7, H7, A8, D8,
H8, A9, A10,

Graphing all valid potential current points

     A B C D E F G H I J
     - - - - - - - - - -
 1 | o o . * o o o o . . |
 2 | o o o o o . o * . . |
 3 | o o o o o o o o . . |
 4 | o o * o o . o * . . |
 5 | o o o o o o o o . . |
 6 | o o . o * o o o . . |
 7 | o o . o . . * o . . |
 8 | o . . o . . . o . . |
 9 | o . . * . . . * . . |
10 | o . . . . . . . . . |
     - - - - - - - - - -
```
