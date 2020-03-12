import sys
import copy
import app.setup

def isSafeFloodFill(v):
    return v == '.' or v == 'O'


def floodfill(pos, grid, numSafe, length):
    if numSafe >= length:
        return numSafe

    y = pos['y'] - 1
    x = pos['x'] - 1
    if isSafeFloodFill(grid[y][x]):
        grid[y][x] = 1
        numSafe = numSafe + 1
        n = safezone(pos, grid, True)
        for i in range(len(n)):
            numSafe = floodfill(n[i], grid, numSafe, length)

    return numSafe

# Check safe spot to go
# beware "* " is part of the body
def isSafetoGo(v, failsafe):
    if failsafe:
        return True
    else:
        return v == '.' or v == 'O'


def safezone(src, grid, failsafe):
    safe = []
    up = {'x': src['x'], 'y': src['y'] - 1}
    down = {'x': src['x'], 'y': src['y'] + 1}
    right = {'x': src['x'] + 1, 'y': src['y']}
    left = {'x': src['x'] - 1, 'y': src['y']}

    # print("up: ", up)
    # print("down: ", down)
    # print("right: ", right)
    # print("left: ", left)


    height = len(grid)
    width = len(grid[1])

    # print("height: ", height)
    # print("width: ", width)

    if 0 < up['y'] <= height:
        if grid[up['y']-1][up['x']-1] == '.' or grid[up['y']-1][up['x']-1] == 'O' or grid[up['y']-1][up['x']-1] == '#':
            print("Grid up position is: ", grid[up['y'] - 1][up['x'] - 1])
            safe.append(up)

    if 0 < down['y'] <= height:
        if grid[down['y'] - 1][down['x'] - 1] == '.' or grid[down['y'] - 1][down['x'] - 1] == 'O' or grid[down['y']-1][down['x']-1] == '#':
            print("Grid down position is: ", grid[down['y'] - 1][down['x'] - 1])
            safe.append(down)

    if 0 < right['x'] <= width:
        if grid[right['y'] - 1][right['x'] - 1] == '.' or grid[right['y'] - 1][right['x'] - 1] == 'O' or grid[right['y']-1][right['x']-1] == '#':
            print("Grid right position is: ", grid[right['y'] - 1][right['x'] - 1])
            safe.append(right)

    if 0 < left['x'] <= width:
        if grid[left['y'] - 1][left['x'] - 1] == '.' or grid[left['y'] - 1][left['x'] - 1] == 'O' or grid[left['y']-1][left['x']-1] == '#':
            print("Grid left position is: ", grid[left['y'] - 1][left['x'] - 1])
            safe.append(left)

    return safe


def heuristic(grid, state, my_moves, enemy_moves):
        score = 0

        # Handle head-on-head collisions
        if state['me']['body'][0]['x'] == state['target']['body'][0]['x'] and state['me']['body'][0]['y'] == state['target']['body'][0]['y']:
            # checking size
            if len(state['me']['body']) > len(state['target']['body']):
                # I am bigger, I win
                print("I am bigger. Go for kill!!!!")
                score = score + 2147483647
            elif len(state['me']['body']) <= len(state['target']['body']):
                print("let's run!!! I am small or same!!!!")
                # I am smaller, I lose
                return -2147483648
            else:
                # It is a draw, we die anyways
                # It is not a bounty snake, you need to win to win
                return -2147483648


        # My win/lose condition
        if len(my_moves) == 0:
            # no more moves, I am trapped
            return -2147483648

        if state['me']['health'] <= 0:
            # out of health
            return -2147483648

        # get all the food position from current state
        food = []
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == 'O':
                    food.append({'x': j, 'y': i})

        floodfill_grid = copy.deepcopy(grid)
        floodfill_grid[state['me']['body'][0]['y']-1][state['me']['body'][0]['x']-1] = '.'
        floodfill_depth = (2 * len(state['me']['body'])) + len(food)
        accessible_squares = floodfill(state['me']['body'][0], floodfill_grid, 0, floodfill_depth)
        percent_accessible = accessible_squares/ float(len(grid)*len(grid[1]))

        # print("accessible_squares: ", accessible_squares)
        # print("percent_accessible", percent_accessible)

        if accessible_squares <= len(state['me']['body']):
            # this can be a death trap
            if percent_accessible != 0:
                return -9999999 * (1 / percent_accessible)
            else:
                return -9999999

        if len(enemy_moves) == 0:
            # enemy have no more move
            score = score + 2147483647

        if state['target']['health'] <= 0:
            # enemy have no more health
            score = score + 2147483647

        enemy_floodfill_grid = copy.deepcopy(grid)
        enemy_floodfill_grid[state['target']['body'][0]['y']-1][state['target']['body'][0]['x']-1] = '.'
        enemy_floodfill_depth = (2 * len(state['target']['body'])) + len(food)
        enemy_accessible_squares = floodfill(state['target']['body'][0], enemy_floodfill_grid, 0, enemy_floodfill_depth)
        enemy_percent_accessible = enemy_accessible_squares / float(len(grid) * len(grid[1]))

        # print("enemy accessible_squares: ", enemy_accessible_squares)
        # print("enemy percent_accessible", enemy_percent_accessible)

        if enemy_accessible_squares <= len(state['target']['body']):
            # target is going for death trap
            score = score + 9999999

        foodweight = 0
        LOW_FOOD = 8
        HUNGER_HEALTH = 40

        if len(food) <= LOW_FOOD:
            foodweight = 200 - (2 * state['me']['health'])
        else:
            if state['me']['health'] <= HUNGER_HEALTH or len(state['me']['body']) < 4:
                foodweight = 100 - state['me']['health']

        if foodweight > 0:
            for i in range(len(food)):
                d = app.setup.Util.mandis(state['me']['body'][0], food[i])
                score = score - (d * foodweight) - i

        # hang out near enemy head
        aggressive_weight = 100
        if len(food) <= LOW_FOOD:
            aggressive_weight = state['me']['health']

        killsquares = safezone(state['target']['body'][0], grid, True)
        enemy_last_direction = app.setup.Util.distance(state['target']['body'][1], state['target']['body'][0])
        for i in range(len(killsquares)):
            dist = app.setup.Util.mandis(state['me']['body'][0], killsquares[i])
            direction = app.setup.Util.distance(state['target']['body'][0], killsquares[i])
            if direction == enemy_last_direction:
                score = score - (dist * (2 * aggressive_weight))
            else:
                score = score - (dist * aggressive_weight)

        # avoid the edge of the board
        if (state['me']['body'][0]['x'] == 1 or
            state['me']['body'][0]['x'] == len(grid[1]) or
            state['me']['body'][0]['y'] == 1 or
            state['me']['body'][0]['y'] == len(grid)):
            score = score - 25000


        if score < 0:
            score = score * (1/percent_accessible)
        elif score > 0:
            score = score * percent_accessible

        # print(score)
        return score

class Algorithm:

    @staticmethod
    def alphabeta(grid, state, depth, alpha, beta, alphaMove, betaMove, maxPlayer, prev_grid, prev_target_move):
        # if depth == 0:
            # print("Depth", depth)
        # print("maxPlayer:", maxPlayer)
        moves = {}
        my_moves = safezone(state['me']['body'][0], grid, True)
        enemy_moves = {}

        # get the target moves
        if maxPlayer:
            enemy_moves = safezone(state['target']['body'][0], grid, True)
        else:
            enemy_moves = prev_target_move

        # True if calculating alpha at this depth, false if calculating beta
        if maxPlayer:
            moves = my_moves
            neck = state['me']['body'][1]
            if neck in moves:
                moves.remove(neck)
            print("my moves:", moves)
        else:
            moves = enemy_moves
            neck = state['target']['body'][1]
            if neck in moves:
                moves.remove(neck)
            # print("enemy moves:", moves)
        # print("me: ", state['me']['body'][1]['x'])
        # print("target: ", state['target']['body'][1]['x'])

        MAX_RECURSION_DEPTH = 5
        # use getrecursionlimit to prevent runtime error

        if (depth == MAX_RECURSION_DEPTH
                or len(moves) == 0
                or state['me']['health'] <= 0 or state['target']['health'] <= 0
                or (state['me']['body'][0]['x'] == state['target']['body'][0]['x'] and state['me']['body'][0]['y'] == state['target']['body'][0]['y'])):


            # if depth == MAX_RECURSION_DEPTH:
               # print("Reach Max depth!!!")
            # else:
                # print("Reach end game state")

            return heuristic(grid, state, my_moves, enemy_moves), None

        if maxPlayer:
            for i in range(len(moves)):
                new_grid = copy.deepcopy(grid)
                new_state = copy.deepcopy(state)
                eating = False

                if new_grid[moves[i]['y']-1][moves[i]['x']-1] == 'O':
                    eating = True
                    new_state['me']['health'] = 100
                else:
                    new_state['me']['health'] = new_state['me']['health'] - 1

                body_length = len(state['me']['body']) - 1
                if (body_length > 1 and
                        (new_state['me']['body'][body_length]['x'] == new_state['me']['body'][body_length]['x'] and
                         new_state['me']['body'][body_length]['y'] == new_state['me']['body'][body_length]['y'])
                ):
                    pass
                else:
                    new_grid[new_state['me']['body'][body_length]['y']][new_state['me']['body'][body_length]['x']] = '.'

                # remove the tail from the state
                new_state['me']['body'].pop()

                # move head in state and on grid
                if body_length > 1:
                    new_grid[new_state['me']['body'][0]['y']-1][new_state['me']['body'][0]['x']-1] = '#'

                new_state['me']['body'].insert(0, moves[i])
                new_grid[moves[i]['y']-1][moves[i]['x']-1] = '@'

                # if eating, add to snake's body
                if eating:
                    x = new_state['me']['body'][body_length-1]['x'] + 1
                    y = new_state['me']['body'][body_length-1]['y'] + 1
                    new_state['me']['body'].append({"x": y, "y": x})
                    eating = False

                # mark whether is safe spot or not
                length = len(new_state['me']['body'])
                me_x = new_state['me']['body'][length-1]['x']
                me_x_other = new_state['me']['body'][length - 2]['x']
                me_y = new_state['me']['body'][length-1]['y']
                me_y_other = new_state['me']['body'][length - 2]['y']
                if length > 1 and me_x == me_x_other and me_y == me_y_other:
                    new_grid[new_state['me']['body'][length-1]['y']-2][new_state['me']['body'][length-1]['x']-2] = '#'
                else:
                    new_grid[new_state['me']['body'][length-1]['y']-2][new_state['me']['body'][length-1]['x']-2] = '*'

                # print out new map
                # app.setup.Util.printMap(new_grid)
                # print("Alpha moves choices: ", moves)

                newAlpha, tempMove = app.algorithm.Algorithm.alphabeta(new_grid, new_state, depth+1, alpha, beta, alphaMove, betaMove, False, grid, enemy_moves)
                if newAlpha > alpha:
                    alpha = newAlpha
                    alphaMove = moves[i]

                if beta <= alpha:
                    break

            # print("alphaMove: ", alphaMove)
            # print("alpha: ", alpha)

            return alpha, alphaMove
        else:
            for i in range(len(moves)):
                new_grid = copy.deepcopy(grid)
                new_state = copy.deepcopy(state)
                eating = False

                if prev_grid[moves[i]['y']-1][moves[i]['x']-1] == 'O':
                    eating = True
                    new_state['target']['health'] = 100
                else:
                    new_state['target']['health'] = new_state['target']['health'] - 1

                body_length = len(state['target']['body']) - 1
                if (body_length > 1 and
                        (new_state['target']['body'][body_length]['x'] == new_state['target']['body'][body_length-1]['x'] and
                         new_state['target']['body'][body_length]['y'] == new_state['target']['body'][body_length-1]['y'])
                ):
                    pass
                else:
                    new_grid[new_state['target']['body'][body_length]['y']][new_state['target']['body'][body_length]['x']] = '.'

                new_state['target']['body'].pop()

                if body_length > 1:
                    new_grid[new_state['target']['body'][0]['y']-1][new_state['target']['body'][0]['x']-1] = '#'

                new_state['target']['body'].insert(0, moves[i])
                new_grid[moves[i]['y']-1][moves[i]['x']-1] = '@'

                if eating:
                    x = new_state['target']['body'][body_length]['x'] + 1
                    y = new_state['target']['body'][body_length]['y'] + 1
                    new_state['target']['body'].append({"x": y, "y": x})
                    eating = False

                # print(new_state)
                length = len(new_state['target']['body'])
                target_x = new_state['target']['body'][length-1]['x']
                target_x_other = new_state['target']['body'][length - 2]['x']
                target_y = new_state['target']['body'][length-1]['y']
                target_y_other = new_state['target']['body'][length - 2]['y']


                if length > 1 and target_x == target_x_other and target_y == target_y_other:
                    new_grid[new_state['target']['body'][length-1]['y']-2][new_state['target']['body'][length-1]['x']-2] = '#'
                else:
                    new_grid[new_state['target']['body'][length-1]['y']-2][new_state['target']['body'][length-1]['x']-2] = '*'

                # print out new map
                # app.setup.Util.printMap(new_grid)

                newBeta, tempMove = app.algorithm.Algorithm.alphabeta(new_grid, new_state, depth + 1, alpha, beta, alphaMove, betaMove, True, {}, {})
                if newBeta < beta:
                    beta = newBeta
                    betaMove = moves[i]

                if beta <= alpha:
                    break

            # print("betaMove: ", betaMove)
            # print("beta: ", beta)

            return beta, betaMove
