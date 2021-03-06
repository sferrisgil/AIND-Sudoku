#from collections import Counter
# We need the method Counter from the collecitons packahge to easily count the
# number of times that a posible twin appears in the associated units
# some initialitation of variables
assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:   
    # We need to create  a sub-dictionary of the values for each unit to change them without affecting the original values
    # of the boxes because of the way Python appoints to the lists and dictionaries while in the loops.
        cunit = dict((z, values[z]) for z in unit)
        counter={} # Initialite a counter as a dictionary, to write down the number of instances that each value appears in the unit
        for y in cunit.values():
            if  not y in counter: counter[y]=1 #the first time always have the value 'one'
            else:  counter[y]+=1 # if we found more values we increment the counter
            twins_values = [c for c in counter if len(c) == 2 and counter[c] == 2]
            # The previous line prevents from taking into account 'triplets' and other rare cases
            # We have built the list of twins values in current unit.Let's discard the substrings containing each of the digits of the twins values
            if len(twins_values) > 0: #We have twins in the unit
                for t in twins_values: # loop through all possible twins (normally one, but theretically maybe more)
                    for u in cunit:
                        if cunit[u] != t: #this assures not to delete the real twin
                            assign_value(values, u, values[u].replace(t[0], '')) #eliminating the first digit of twins from the current unit
                            assign_value(values, u, values[u].replace(t[1], '')) #eliminating the second digit of twins from the current unit
                            # If the rest of unit's boxes don't contain any of the digits of the twin, replace method leave their values unaltered               
    return values


def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

# here go some auxiliary variables that we are going to use in other functions below  to solve the Sudoku
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# diagonal_units = define the two diagonal units
# diagonal_units = define the two diagonal units.  I assume a  square matrix
l = int(len(boxes)**0.5)  # length is the square root of the length of dictionary
diagonal_unit1 = [boxes[i*l+i] for i in list(range(l))]   #backward slash main diagonal          
diagonal_unit2 = [boxes[i*(l-1)+ (l-1)] for i in list(range(l-1,-1,-1))]  #forward slash main diagonal
diagonal_units = [diagonal_unit1 , diagonal_unit2] #list of diagonals

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
# units and peers now include diagonal units

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
        Keys: The boxes, e.g., 'A1'
        Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            chars.append(all_digits)
        elif c in all_digits:
            chars.append(c)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    print('values: ',values)
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
        for c in cols))
        if r in 'CF': print(line)
    return   
    
def eliminate(values):
    """
    This is the primary rule to solve a Sudoku. No digit can be in the same unit twice!
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    The second strategy to solve a Sudoku. If a unit has a box where only fits
    one value, put that value there and take out this calue from the rest of the
    unit. Do the same through all the units.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice() and also naked_twins. If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    Any addional strategy must be placed here
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        #adding the naked_twins strategy
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            print("This Sudoku has no solution")
            return False
    return values

def search(values):
    values = reduce_puzzle(values)
    print ('type(reduce_puzzle(values)) ', type(reduce_puzzle(values)))
    print ('values: ', values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    dict_sudoku = grid_values(grid)
    sudoku = search(dict_sudoku)
    if not sudoku:
        return False
    else:
        return sudoku
        

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

