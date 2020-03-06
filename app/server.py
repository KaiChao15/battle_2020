import json
import os
import random

import bottle
from bottle import HTTPResponse


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    print("START:", json.dumps(data))

    response = {"color": "#00FF00", "headType": "regular", "tailType": "regular"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    data = bottle.request.json

    # decode the JSON file
    temp_data = json.dumps(data)
    game_state = json.loads(temp_data)
    print("========MOVE==========")
    print(game_state)

    # Convert into one-based coordinates
    # food
    for i in range(len(game_state['board']['food'])):
        game_state['board']['food'][i]['x'] = game_state['board']['food'][i]['x'] + 1
        game_state['board']['food'][i]['y'] = game_state['board']['food'][i]['y'] + 1

    # snakes
    for i in range(len(game_state['board']['snakes'])):
        for j in range(len(game_state['board']['snakes'][i]['body'])):
            game_state['board']['snakes'][i]['body'][j]['x'] = game_state['board']['snakes'][i]['body'][j]['x'] + 1
            game_state['board']['snakes'][i]['body'][j]['y'] = game_state['board']['snakes'][i]['body'][j]['y'] + 1

    # you
    for i in range(len(game_state['you']['body'])):
        game_state['you']['body'][i]['x'] = game_state['you']['body'][i]['x'] + 1
        game_state['you']['body'][i]['y'] = game_state['you']['body'][i]['y'] + 1

    print("Finish converting -- PASSED")

    grid = app.setup.Util.buildWorldMap(game_state)
    print("Building World Map... -- PASSED")

    # print out the current game state map
    # app.setup.Util.printMap(grid)
    # print("Print out World Map... -- PASSED")

    # decide the enemy snake, beta testing use myself as prediction
    me = game_state['you']
    target = None
    target_dis = 99999
    if len(game_state['board']['snakes']) >= 2:
        print("There are more than 2 snakes. Choose the closest one to predict it's move.")

        for i in range(len(game_state['board']['snakes'])):
            # check the target is not myself
            if game_state['board']['snakes'][i]['id'] != me['id']:
                d = app.setup.Util.mandis(me['body'][1], game_state['board']['snakes'][i]['body'][1])

                if d < target_dis:
                    target_dis = d
                    target = game_state['board']['snakes'][i]

    else:
        # only one snake on the board (myself)
        # This is not working (always head collision)
        print("I am choosing myself.")
        target = me

    cur_state = {'me': me, 'target': target}
    print("Finding target -- PASSED")
    print("Me(main): ", cur_state['me'])
    print("Target(main): ", cur_state['target'])

    print("Start to find the best solution...")
    bestScore, bestMove = app.algorithm.Algorithm.alphabeta(grid, cur_state, 0, -2147483647, 2147483647, None, None, True, {}, {})

    print("Best Score: " + str(bestScore))
    print("Best move ", bestMove)
    print("My current position: ", me['body'][0])

    direction = app.setup.Util.distance(me['body'][0], bestMove)
    print("direction", direction)

    shout = "I am Kai's snake!"
    response = {"move": direction, "shout": shout}

    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
