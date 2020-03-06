
class Util:
    def __init__(self, game_state):
        self.game_state = game_state

    @staticmethod
    def buildWorldMap(game_state):
        # generate the tile grid
        print("generating the tile grid...")
        board = game_state['board']
        w, h = board['width'], board['height']
        grid = [[0 for x in range(w)] for y in range(h)]
        for i in range(h):
            for j in range(w):
                grid[i][j] = '.'

        # place food
        food_amount = len(board['food'])
        for i in range(food_amount):
            x = board['food'][i]['x'] - 1
            y = board['food'][i]['y'] - 1
            grid[y][x] = 'O'

        # place snakes
        snake_amount = len(board['snakes'])
        for i in range(snake_amount):
            body_length = len(board['snakes'][i]['body'])
            for j in range(body_length):
                # head
                if j == 0:
                    x = board['snakes'][i]['body'][j]['x'] - 1
                    y = board['snakes'][i]['body'][j]['y'] - 1
                    grid[y][x] = '@'
                # tail
                elif j == body_length - 2:
                    x = board['snakes'][i]['body'][j]['x'] - 1
                    y = board['snakes'][i]['body'][j]['y'] - 1
                    grid[y][x] = '*'
                # body
                else:
                    x = board['snakes'][i]['body'][j]['x'] - 1
                    y = board['snakes'][i]['body'][j]['y'] - 1
                    grid[y][x] = '#'

        return grid

    @staticmethod
    def printMap(grid):
        check_grid = []
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                check_grid.append(grid[i][j])
            print(check_grid)
            print()
            check_grid = []

    # Calculates the manhattan distance between two coordinate pairs
    @staticmethod
    def mandis(src, dist):
        dx = abs(src['x'] - dist['x'])
        dy = abs(src['y'] - dist['y'])
        return dx + dy

    @staticmethod
    def distance(src, dst):
        if dst['x'] == src['x'] + 1 and dst['y'] == src['y']:
            return 'right'
        elif dst['x'] == src['x'] - 1 and dst['y'] == src['y']:
            return 'left'
        elif dst['x'] == src['x'] and dst['y'] == src['y'] + 1:
            return 'down'
        elif dst['x'] == src['x'] and dst['y'] == src['y'] - 1:
            return 'up'
        else:
            print("what the hell?? Got a weird input!!!!!!!")
            return 'up'
