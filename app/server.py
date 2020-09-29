import json
import os
import time
import random

import cherrypy

import app.setup
import app.algorithm

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "Rubelliguis",
            "color": "#ff3838",
            "head": "bwc-earmuffs",
            "tail": "hook",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        start = time.time()
        data = cherrypy.request.json

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
                    d = app.setup.Util.mandis(me['body'][0], game_state['board']['snakes'][i]['body'][0])

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
        bestScore, bestMove = app.algorithm.Algorithm.alphabeta(grid, cur_state, 0, -2147483647, 2147483647, None, None,
                                                                True, {}, {})

        print("Best Score: " + str(bestScore))
        print("Best move ", bestMove)
        print("My current position: ", me['body'][0])

        # There are no bestMove, just chose one safe option to go.
        if bestMove is None:
            betterMove = app.algorithm.safezone(cur_state['me']['body'][0], grid, True)
            print("No best move from the alpha-beta... Try better choice!")
            print("Better choice: ", betterMove)
            bestMove = random.choice(betterMove)

        direction = app.setup.Util.distance(me['body'][0], bestMove)
        print("direction", direction)

        # respond time
        end = time.time()
        total_time = end - start
        print("Time takes: ", total_time)


        print(f"MOVE: {direction}")
        return {"move": direction}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
