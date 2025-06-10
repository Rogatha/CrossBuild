from CrossBuild import *



class CrosswordGridTestingUnit():
    def __init__(self, size, parameters):
        """A unit for testing the CrosswordGrid class.
        Parameters:
            A tuple containing the parameters for the grid generation. in the order:
                - max_black_squares_p
                - min_black_squares_p
                - iterations_per_try
                - max_iterations
                - default_black_square_weight
                - default_black_island_weight
                - default_black_island_row_col_weight
                - default_black_island_row_col_weight_offset
        """

        self.score = None
        self.parameters = parameters
        self.grid = CrosswordGrid(size[0], size[1])

        self.success = self.grid.generate_black_squares(*self.parameters)




def main():
    max_black_squares_p=0.3
    min_black_squares_p=0.2
    iterations_per_try=100
    max_iterations=100
    default_black_square_weight=0.75
    default_black_island_weight=0.4
    default_black_island_row_col_weight=0.011
    default_black_island_row_col_weight_offset=0.335

    parameter_successfulness = {}

    sucessfulness = 0
    for _ in range(100):
        parameters = (max_black_squares_p, min_black_squares_p, iterations_per_try, max_iterations,
                      default_black_square_weight, default_black_island_weight,
                      default_black_island_row_col_weight, default_black_island_row_col_weight_offset)
        unit = CrosswordGridTestingUnit((10, 10), parameters)
        if unit.success:
            sucessfulness += 1
    
    success_rate = sucessfulness / 100
    if 





if __name__ == "__main__":
    main()