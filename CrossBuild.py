import random


"""TO DO:
1. import and clean up word lists for use in WordList.txt and ClueDict.csv
2. Test WordList and ClueDict classes
3. Optimize parameters for CrosswordGrid.generate_black_squares() method
4. Implement CrosswordPuzzle.generate_clues() method
5. Import PyGame and implement GUI for crossword puzzle generation
6. Add file headers and a README"""



def generate_random_numbers(n, min_value, max_value):
    """Generates a list of n random numbers between min_value and max_value."""
    return [random.randint(min_value, max_value) for _ in range(n)]

class CrosswordWord:
    def __init__(self, row, col, direction, word="TEST", clue="TEST", word_length=0):
        """Direction is either 'horizontal' or 'vertical'."""
        self.word = word
        self.clue = clue
        self.row = row
        self.col = col
        self.direction = direction

        self.length = word_length if word_length else len(word)
    
    def __hash__(self):
        """Returns a hash of the crossword word."""
        return hash((self.word, self.row, self.col, self.direction))
    
    def __eq__(self, other):
        """Checks if two crossword words are equal."""
        return (self.word == other.word and 
                self.row == other.row and 
                self.col == other.col and 
                self.direction == other.direction)
    
    def __str__(self):
        """Returns a string representation of the crossword word."""
        return self.word + '(' + str(self.length) + ')'


class CrosswordGrid:
    def __init__(self, size):
        """Size is a tuple (rows, columns) representing the grid dimensions."""
        self.size = size
        self.grid = [[' ' for _ in range(size[0])] for _ in range(size[1])]

        self.mini = False
        if self.size[0] <= 10 or self.size[1] <= 10:
            self.mini = True

        self.num_black_squares = 0
        self.black_square_percentage = 0
        self.across_words = {} #To be populated with CrosswordWord objects
        self.down_words = {} #Same here

    def generate_black_squares(self, max_black_squares_p=0.225, min_black_squares_p=0.175, iterations_per_try=100,
                               max_iterations=100, default_black_square_weight=0.75, 
                               default_black_island_weight=0.4, default_black_island_row_col_weight=0.011,
                               default_black_island_row_col_weight_offset=0.335, row_col_reset_chance=0.25, 
                               max_word_count=152):
        """Generates a grid with black squares (represented by '#') and white squares (represented by '•').
        Rules for crossword grids:
        1. All words must be at least 3 letters long.
        2. All letters in all words must cross another word.
        3. All black squares must be rotationally symmetric.
        4. Black squares must not occupy more than 20% of the grid.
        5. The whole grid must be coninuously connected.
        """

        black_squares_count = 0

        if not self.mini:
            black_squares_count = self.place_edge_black_squares()
        else:
            print("Cannot handle minis yet...")
            raise Exception

        total_cells = self.size[0] * self.size[1]
        max_black_squares = int(total_cells * max_black_squares_p)
        min_black_squares = int(total_cells * min_black_squares_p)

        iterations = 0
        #Random placement of interior squares until an acceptable number of black squares is reached
        while black_squares_count < min_black_squares:
            iterations += 1
            if iterations > iterations_per_try:
                print("Failed to generate a valid crossword grid after 100 iterations. Restarting...")
                self.reset()
                return self.generate_black_squares()

            cols_to_search = self.size[1] - 1
            # low_range = 0 if iterations > 2 else 1
            for row in range(1, self.size[0]):
                cols_to_search -= 1
                for col in range(1, cols_to_search):
                    if self.grid[row][col] == '#':
                        continue
                    black_square_weight = default_black_square_weight #Default weight for black square placement

                    if row != 1 and col != 1: #Only adjust black square weight if not in second row or column
                        black_island_weight = default_black_island_weight * self.black_island_size(row, col)  #Weight based on the size of the black square island
                        black_square_weight -= black_island_weight #Decrease weight based on the size of the black square island

                        black_islands_in_row = self.black_islands_in_row(row)
                        black_islands_in_col = self.black_islands_in_col(col)
                        black_island_row_weight = default_black_island_row_col_weight * self.size[0] - default_black_island_row_col_weight_offset
                        black_island_col_weight = default_black_island_row_col_weight * self.size[1] - default_black_island_row_col_weight_offset
                        black_square_weight -= black_islands_in_row * black_island_row_weight #Decrease weight based on black squares in the row
                        black_square_weight -= black_islands_in_col * black_island_col_weight #Decrease weight based on black squares in the column

                    if random.random() < black_square_weight \
                    and self.validate_black_square(row, col, black_squares_count, max_black_squares):
                        self.grid[row][col] = '#'
                        self.grid[self.size[0] - 1 - row][self.size[1] - 1 - col] = '#'

                        if row == self.size[0] -1 - row and col == self.size[1] - 1 - col:
                            black_square_count += 1 #There is no symmetric counterpart
                        else:
                            black_squares_count += 2  #Count both the square and its symmetric counterpart
            
            #Randomly delete the center row or column of the grid
            if random.random() < row_col_reset_chance:
                odd_rows = False
                odd_cols = False
                if self.size[0] % 2 == 1:  #Odd number of rows
                    odd_rows = True
                if self.size[1] % 2 == 1:
                    odd_cols = True
                if odd_rows and odd_cols:
                    if random.random() < 0.5:
                        row = self.size[0] // 2
                        for col in range(self.size[1]):
                            if self.grid[row][col] == '#':
                                black_squares_count -= 1
                            self.grid[row][col] = ' '
                    else:
                        col = self.size[1] // 2
                        for row in range(self.size[0]):
                            if self.grid[row][col] == '#':
                                black_squares_count -= 1
                            self.grid[row][col] = ' '
                elif odd_rows:  #Odd number of rows, even number of columns
                    row = self.size[0] // 2
                    for col in range(self.size[1]):
                        if self.grid[row][col] == '#':
                            black_squares_count -= 1
                        self.grid[row][col] = ' '
                elif odd_cols:  #Even number of rows, odd number of columns
                    col = self.size[1] // 2
                    for row in range(self.size[0]):
                        if self.grid[row][col] == '#':
                            black_squares_count -= 1
                        self.grid[row][col] = ' '

            
            self.num_black_squares = black_squares_count
            self.black_square_proportion = round(black_squares_count / total_cells, 3)

        #If the number of black squares exceeds the maximum allowed, reset and try again
        if black_squares_count > max_black_squares:
            print("Exceeded maximum number of black squares. Resetting...")
            self.reset()
            return self.generate_black_squares()
        
        #If no black squares in row 3 and column 3, reset and try again
        if self.black_islands_in_row(2) == 0 and self.black_islands_in_col(2) == 0:
            print("No black squares in row 3 and column 3. Resetting...")
            self.reset()
            return self.generate_black_squares()
        elif self.black_islands_in_row(2) == 0:
            if random.random() < 0.75:
                print("No black squares in row 3. Resetting...")
                self.reset()
                return self.generate_black_squares()
        elif self.black_islands_in_col(2) == 0:
            if random.random() < 0.75:
                print("No black squares in column 3. Resetting...")
                self.reset()
                return self.generate_black_squares()
        
        self.update_words()  # Update the words after placing black squares"""
        
        if len(self.across_words) + len(self.down_words) > max_word_count:
            print("Exceeded maximum number of words. Resetting...")
            self.reset()
            return self.generate_black_squares()
        
        return True

    def place_edge_black_squares(self):
        """Places edge squares on the top and left edge of the grid. Assumes that the grid is not a mini."""

        black_square_count = 0

        #Place black squares on the top row
        black_square_probability = 0.25
        steps_since_last_black = 0
        for col in range(3, self.size[0] - 3):
            if random.random() < black_square_probability:
                self.grid[0][col] = '#'
                self.grid[self.size[0] - 1][self.size[1] - 1 - col] = '#'
                black_square_probability = 0
                steps_since_last_black = 0
                black_square_count += 2
            elif steps_since_last_black >= 3:
                black_square_probability += 0.25
                steps_since_last_black += 1
            else:
                steps_since_last_black += 1

        #Place black squares on the left edge
        black_square_probability = 0.25
        steps_since_last_black = 0
        for row in range(3, self.size[1] - 3):
            if random.random() < black_square_probability:
                self.grid[row][0] = '#'
                self.grid[self.size[0] - 1 - row][self.size[1] - 1] = '#'
                black_square_probability = 0
                steps_since_last_black = 0
                black_square_count += 2
            elif steps_since_last_black >= 3:
                black_square_probability += 0.25
                steps_since_last_black += 1
            else:
                steps_since_last_black += 1
        
        return black_square_count


    def validate_black_square(self, row, col, black_squares_count, max_black_squares):
        """Returns True if a black square can be placed at (row, col) without violating the rules,
        False, otherwise"""

        #Populate the grid with a black square at (row, col) and its symmetric counterpart
        symmetric_row = self.size[0] - 1 - row
        symmetric_col = self.size[1] - 1 - col
        self.grid[row][col] = '#'
        self.grid[symmetric_row][symmetric_col] = '#'

        #Ensure that placing black squares does not exceed the maximum allowed
        if black_squares_count >= max_black_squares:
            self.grid[row][col] = '•'
            self.grid[symmetric_row][symmetric_col] = '•'
            return False
        
        #Make sure this black square or its symmetric counterpart does not create any words 
        #that are less than 3 letters long
        for test_row, test_col in [(row, col), (symmetric_row, symmetric_col)]:
            for dir in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
                count = 0
                r, c = test_row + dir[0], test_col + dir[1]
                while 0 <= r < self.size[0] and 0 <= c < self.size[1] and self.grid[r][c] != '#':
                    count += 1
                    r += dir[0]
                    c += dir[1]
                if count < 3 and count != 0:
                    self.grid[row][col] = '•'
                    self.grid[symmetric_row][symmetric_col] = '•'
                    return False
        
        #Make sure all letters are seen by two words (Check all letters in all new words that are 
        #created by placing this black square)
        for test_row, test_col in [(row, col), (symmetric_row, symmetric_col)]:
            for dir in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
                r, c = test_row + dir[0], test_col + dir[1]
                if 0 <= r < self.size[0] and 0 <= c < self.size[1] and self.grid[r][c] != '#':
                    if not self.is_crossed(r, c):
                        self.grid[row][col] = '•'
                        self.grid[symmetric_row][symmetric_col] = '•'
                        return False
                    
                    r += dir[0]
                    c += dir[1]
                
                r += dir[0]
                c += dir[1]

        #Make sure grid is continuously connected
        if not self.connected((0, 0), (self.size[0] - 1, self.size[1] - 1)):
            self.grid[row][col] = '•'
            self.grid[symmetric_row][symmetric_col] = '•'
            return False

        return True
    
    def good_edge_coverage(self, num_islands):
        """Checks to make sure there are at least the given number of islands of black squares on 
        each edge of the grid."""
        islands = 0
        new_island = True
        for row in range(self.size[0]):
            if self.grid[row][0] == '#':
                if new_island:
                    islands += 1
                    new_island = False
            else:
                new_island = True
        
        return islands >= num_islands
    
    def black_islands_in_row(self, row):
        """Returns the number of black square islands in the given row."""
        islands = 0
        new_island = True
        for col in range(self.size[1]):
            if self.grid[row][col] == '#':
                if new_island:
                    islands += 1
                    new_island = False
            else:
                new_island = True
        
        return islands
    
    def black_islands_in_col(self, col):
        """Returns the number of black square islands in the given column."""
        islands = 0
        new_island = True
        for row in range(self.size[0]):
            if self.grid[row][col] == '#':
                if new_island:
                    islands += 1
                    new_island = False
            else:
                new_island = True
        
        return islands
    
    def black_island_size(self, row, col):
        """Returns the size of the black square island at the given location in the grid assuming
        (row, col) is a black square even if it is not."""

        visited = set()
        queue = [(row, col)]
        island_size = 0

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            island_size += 1

            for d in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_row, next_col = current[0] + d[0], current[1] + d[1]
                if self.in_grid(next_row, next_col) and self.grid[next_row][next_col] == '#':
                    if (next_row, next_col) not in visited:
                        queue.append((next_row, next_col))
        
        return island_size
    
    def is_crossed(self, row, col):
        """Returns True if the letter at (row, col) is crossed by two words, False otherwise.
        Does not check the length of the crossing words."""
        
        word_count = 0

        for dir in ([0, 1], [1, 0]):
            r_pos, c_pos = row + dir[0], col + dir[0]
            r_neg, c_neg = row - dir[0], col - dir[1]
            if self.in_grid(r_pos, c_pos) and self.grid[r_pos][c_pos] != '#' \
            or self.in_grid(r_neg, c_neg) and self.grid[r_neg][c_neg] != '#':
                word_count += 1

        return word_count == 2
    
    def update_words(self):
        """Updates the word dictionaries based on the current grid state."""
        self.across_words.clear()
        self.down_words.clear()

        word_count = 0
        across_word = False

        for row in range(self.size[0]):
            for col in range(self.size[1]):
                left = (row, col - 1)
                up = (row - 1, col)

                # Skip if the cell is a black square
                if self.grid[row][col] != '#':
                    #Check across words
                    if not self.in_grid(left[0], left[1]) or self.grid[left[0]][left[1]] == '#':
                        # Start of an across word
                        word_count += 1
                        across_word = True
                        word, word_length = self.get_word(row, col, 'across', length=True)
                        self.across_words[str(word_count) + 'A'] = (CrosswordWord(row, col, 'across', word=word, word_length=word_length))
                    
                    #Check down words
                    if not self.in_grid(up[0], up[1]) or self.grid[up[0]][up[1]] == '#':
                        # Start of a down word
                        if not across_word:
                            word_count += 1
                        word, word_length = self.get_word(row, col, 'down', length=True)
                        self.down_words[str(word_count) + 'D'] = (CrosswordWord(row, col, 'down', word=word, word_length=word_length))
                    across_word = False  # Reset across word flag for the next cell

    def get_word(self, row, col, direction, length=False):
        """Returns the word starting at (row, col) in the specified direction ('across' or 'down').
        Also returns the length of the word if length=True."""
        word = ""
        word_length = 0
        if direction == 'across':
            for c in range(col, self.size[1] + 1):
                if not self.in_grid(row, c) or self.grid[row][c] == '#':
                    if length:
                        return word, word_length
                    return word
                
                word += self.grid[row][c]
                word_length += 1
        elif direction == 'down':
            for r in range(row, self.size[0] + 1):
                if not self.in_grid(r, col) or self.grid[r][col] == '#':
                    if length:
                        return word, word_length
                    return word
                
                word += self.grid[r][col]
                word_length += 1
        else:
            raise ValueError("Direction must be 'across' or 'down'.")
                
    def add_word(self, word, row, col, direction):
        pass

    def connected(self, start, end):
        """Checks if the grid is continuously connected from start to end using BFS."""
        visited = set()
        queue = [start]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return True
            
            for d in directions:
                next_row, next_col = current[0] + d[0], current[1] + d[1]
                if self.in_grid(next_row, next_col) and self.grid[next_row][next_col] != '#':
                    queue.append((next_row, next_col))
        return False

    def in_grid(self, row, col):
        """Returns True if (row, col) is within the grid boundaries, False otherwise."""
        return 0 <= row < self.size[0] and 0 <= col < self.size[1]
    
    def reset(self):
        """Resets the crossword grid to its initial state."""
        self.grid = [['•' for _ in range(self.size[1])] for _ in range(self.size[0])]
        self.num_black_squares = 0
        self.black_square_percentage = 0
        self.across_words.clear()
        self.down_words.clear()

    def display(self, info=False):
        print('+' + '---' * self.size[1] + '+')
        for row in self.grid:
            row_output = ""
            row_output += '|'
            for item in row:
                if item == '#':
                    row_output += "▮▮▮"
                else:
                    row_output += f" {item} "
            row_output += '|'
            print(row_output)
        print('+' + '---' * self.size[1] + '+')

        if info:
            print(f"Grid size: {self.size[0]} rows x {self.size[1]} columns")
            print(f"Number of black squares: {self.num_black_squares}")
            print(f"Black square proportion: {self.black_square_proportion:.2%}")
            print(f"Total words: {len(self.across_words) + len(self.down_words)}")

    def print_words(self):
        """Prints all words in the crossword grid."""
        print("Across Words:")
        for key, word in self.across_words.items():
            print(f"{key}: {word}")

        print("\nDown Words:")
        for key, word in self.down_words.items():
            print(f"{key}: {word}")

    def __hash__(self):
        """Returns a hash of the crossword grid."""
        return hash(tuple(tuple(row) for row in self.grid))

    def write_to_file(self, filename=""):
        """Writes the crossword grid to a file."""
        if not filename:
            filename = str(self.__hash__()) + ".txt"

        filepath = "Grids/" + filename 
        
        with open(filepath, 'w') as f:
            for row in self.grid:
                f.write(row + '\n')
    
    def read_from_file(self, filepath):
        """Reads the crossword grid from a file."""
        with open(filepath, 'r') as f:
            self.grid = [list(line.strip()) for line in f.readlines()]
            self.size = (len(self.grid), len(self.grid[0])) if self.grid else (0, 0)
        

class CrosswordPuzzle():
    def __init__(self, grid):
        """Initializes a crossword puzzle with a given grid."""
        self.grid = grid
        self.clue_dict = {}  # To be populated with clues for the words
        self.word_list = []  # To be populated with words from the grid

    def generate_clues(self):
        """Generates clues for the words in the crossword puzzle."""
        pass  # Implementation to be added later

    def display_grid(self):
        """Displays the crossword puzzle."""
        self.grid.display(info=True)

    def display_clues(self):
        """Displays the clues for the crossword puzzle."""
        print("Clues:")
        for key, word in self.grid.across_words.items():
            print(f"{key} (Across): {word.clue}")
        for key, word in self.grid.down_words.items():
            print(f"{key} (Down): {word.clue}")


def main():
    size = (21, 21)  # Example size
    grid = CrosswordGrid(size)
    grid.generate_black_squares()
    grid.display(info=True)
    grid.print_words()



if __name__ == "__main__":
    main()