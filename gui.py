import pygame
import threading
from ClueDatabase import *
from CrossBuild import *


class Worker:
    def __init__(self, executable, *args, **kwargs):
        """
        Initialize the worker with an executable, but don't start it until run() is called.

        :param executable: The callable task to run.
        :param args: Positional arguments for the task.
        :param kwargs: Keyword arguments for the task.
        """
        self.executable = executable
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
        self.result = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._started = False

    def start(self):
        """Start the worker thread if it hasn't already been started."""
        if not self._started:
            self._thread.start()
            self._started = True

    def _run(self):
        """Internal method that executes the task and sets the finished flag."""
        try:
            self.result = self.executable(*self.args, **self.kwargs)
        except Exception as e:
            print(f"[Worker] Error during execution: {e}")
        finally:
            self.finished.set()
    


class DisplayGridSquare():
    """each individual square in a DisplayGrid object."""

    def __init__(self, label=None, letter=None, circle=False, shading=False):
        """initializes a DisplayGridSquare object.
        label: '24D'
        letter: 'P' or ' ' for blank
        circle: true for circle in non-black square
        shading: true for shading in non-black square"""

        self.label = label
        self.letter = letter
        self.circle = circle
        self.shading = shading

        self.color = "white"
        if not letter:
            self.color = "black"
        elif self.shading:
            self.color = "gray"

    def set_label(self, label):
        self.label = label

    def display(self, screen, location, square_size):
        color = self.color
        #Outline
        pygame.draw.rect(screen, "black", (location[1], location[0], square_size, square_size), 1)
        #Square
        pygame.draw.rect(screen, color, (location[1] + 1, location[0] + 1, square_size - 2, square_size - 2))


class DisplayGrid():
    """Crossword grid purely for displaying in pygame"""

    def __init__(self, crossword):
        """Creates the display grid using a CrossBuild.CrosswordGrid object as input"""

        self.grid = [[None for _ in range(crossword.size[1])] for _ in range(crossword.size[0])]
        self.size = crossword.size

        for row in range(self.size[0]):
            for col in range(self.size[1]):
                letter = crossword.grid[row][col] if crossword.grid[row][col] != '#' else None

                self.grid[row][col] = DisplayGridSquare(letter=letter)
        
        for across_word in crossword.across_words.keys():
            row = crossword.across_words[across_word].row
            col = crossword.across_words[across_word].col

            self.grid[row][col].set_label(across_word) 

        for down_word in crossword.down_words.keys():
            row = crossword.down_words[down_word].row
            col = crossword.down_words[down_word].col

            self.grid[row][col].set_label(down_word) 
    
    def display(self, screen, panel_location, panel_size, margin=10):
        """Displays the DisplayGrid onto the given pygame screen. panel_location is 
        the (x, y) or (left, top) of the panel and panel_location is the (width, height) of the panel
        the crossword is to be displayed in. The margin is the space around the grid in pixels."""

        # Size of each cell in pixels
        square_size = min((panel_size[0] - 2 * margin) // self.size[1],
                        (panel_size[1] - 2 * margin) // self.size[0])

        #Draw each individual square in the grid
        for row in range(self.size[0]):
            for col in range(self.size[1]):
                row_pixel = row * (square_size) + margin + panel_location[1]
                col_pixel = col * (square_size) + margin + panel_location[0]
                self.grid[row][col].display(screen, (row_pixel, col_pixel), square_size)


class Panel():
    """A class to represent a panel in the pygame application window."""

    def __init__(self, name, location, size, background_color="gray"):
        self.name = name
        self.location = location  # (x, y)
        self.size = size  # (width, height)
        self.background_color = background_color  # Default background color

    def overlap(self, other):
        """Check if this panel overlaps with another panel."""
        return (self.location[0] < other.location[0] + other.size[0] and
                self.location[0] + self.size[0] > other.location[0] and
                self.location[1] < other.location[1] + other.size[1] and
                self.location[1] + self.size[1] > other.location[1])
    
    def contains(self, point):
        """Check if a point (x, y) is within this panel."""
        return (self.location[0] <= point[0] < self.location[0] + self.size[0] and
                self.location[1] <= point[1] < self.location[1] + self.size[1])

    def display(self, screen):
        """Draw the panel on the given pygame screen."""
        pygame.draw.rect(screen, self.background_color, (self.location[0], self.location[1], self.size[0], self.size[1]), 0)
        font = pygame.font.Font(None, 36)
        text = font.render(self.name, True, "black")
        text_rect = text.get_rect(center=(self.location[0] + self.size[0] // 2, self.location[1] + self.size[1] // 2))
        screen.blit(text, text_rect)

    def __repr__(self):
        return f"Window(name={self.name}, location={self.location}, size={self.size})"

def draw_panels(screen, panels):
    """Draws the panels on the given pygame screen."""
    for panel in panels.values():
        panel.display(screen)

def draw_current_grid(screen, crossword_panel, display_grid):
    """Draws the crossword grid and display grid onto the pygame screen."""
    crossword_panel.display(screen)  # Display the crossword panel
    display_grid.display(screen, crossword_panel.location, crossword_panel.size)  # Display the grid
    pygame.display.flip()  # Update the display to show the changes

def create_crossword(size, parameters=(0.3, 0.2, 100, 100, 0.75, 0.4, 0.011, 0.335)):
    """Create a crossword grid with the given size and parameters. Default parameters are provided."""
    grid = CrosswordGrid(size)
    success = grid.generate_black_squares(*parameters)
    if success:
        return grid
    else:
        raise ValueError("Failed to generate crossword grid with the given parameters.")

def main():
    # pygame setup
    pygame.init()
    screen_height = 720
    screen_width = 1280
    min_window_size = (800, 600)

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("CrossBuild")

    clock = pygame.time.Clock()
    running = True

    panels = {"menu bar": Panel("menu", (0, 0), (screen_width, screen_height // 10), "darkgray"),
              "crossword": Panel("crossword", (0, screen_height // 10), (2 * screen_width // 3, screen_height - screen_height // 10), "lightgray"),
              "workflow": Panel("workflow", (screen_width - screen_width // 3, screen_height // 10), (screen_width // 3, screen_height - screen_height // 10 - screen_height // 40), "gray"),
              "status bar": Panel("status", (screen_width - screen_width // 3, screen_height - screen_height // 40), (screen_width, screen_height // 10), "darkgray")}
    
    screen.fill("gray")
    draw_panels(screen, panels)
    crossword = CrosswordGrid((21, 21))
    crossword.display()
    display_grid = DisplayGrid(crossword)
    display_grid.display(screen, panels["crossword"].location, panels["crossword"].size)
    draw_current_grid(screen, panels["crossword"], display_grid)

    crossword_builder_thread = Worker(create_crossword, size=(21, 21))

    while running:
        # poll for events

        #Display the crossword grid if the crossword builder thread has finished
        if crossword_builder_thread.finished.is_set():
            if crossword_builder_thread.result is not None:
                crossword = crossword_builder_thread.result

            crossword.display(info=True)
            display_grid = DisplayGrid(crossword)
            display_grid.display(screen, panels["crossword"].location, panels["crossword"].size)
            #Display the updated screen 
            pygame.display.flip()
            crossword_builder_thread = Worker(create_crossword, size=(21, 21))  # Reset the thread for the next crossword generation

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                #Ensure the window is not smaller than the minimum size
                if event.w < min_window_size[0] or event.h < min_window_size[1]:
                    event.w = max(event.w, min_window_size[0])
                    event.h = max(event.h, min_window_size[1])

                #Resize the pygame display surface
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                #Update the panels with the new size
                panels["menu bar"].size = (event.w, event.h // 10)
                panels["crossword"].size = (2 * event.w // 3, event.h - event.h // 10)
                panels["crossword"].location = (0, event.h // 10)
                panels["workflow"].location = (event.w - event.w // 3, event.h // 10)
                panels["workflow"].size = (event.w // 3, event.h - event.h // 10)
                panels["status bar"].location = (event.w - event.w // 3, event.h - event.h // 40)
                panels["status bar"].size = (event.w, event.h // 10)
                draw_panels(screen, panels)
                draw_current_grid(screen, panels["crossword"], display_grid)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Exit the program when escape is pressed
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Regenerate the crossword when space is pressed using the worker thread
                    crossword_builder_thread.start()  # Start the crossword builder thread
                    font = pygame.font.Font(None, 36)
                    text = font.render("Generating black squares...", True, "black")
                    text_center = (panels["status bar"].location[0] + 50, panels["workflow"].location[1] + 50)
                    text_rect = text.get_rect(center=text_center)
                    screen.blit(text, text_rect)
                    pygame.display.flip()


            

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


if __name__ == "__main__":
    main()