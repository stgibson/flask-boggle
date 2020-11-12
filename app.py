from boggle import Boggle
from flask import Flask, request, render_template, redirect, session
from flask import make_response, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "kubrick"
# app.config["TESTING"] = True
# app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]

# debug = DebugToolbarExtension(app)

boggle_game = Boggle()

@app.route("/")
def show_game_page():
    """
        Shows the page for the website
        rtype: str
    """
    # if necessary session values are not set, set them to 0
    session["highscore"] = session.get("highscore", 0)
    session["num_of_times_played"] = session.get("num_of_times_played", 0)

    return render_template("home.html")

@app.route("/game")
def start_game():
    """
        This starts the game and creates the game board with the dimensions
        provided by the user
        rtype: json
    """
    size = int(request.args["dimensions"])
    board = boggle_game.make_board(size)
    session["board"] = board
    return render_template("game.html")

@app.route("/guess", methods=["POST"])
def check_guess():
    """
        Check if a guess made by the user is a valid word and is in the board
        rtype: json
    """
    data = request.get_json()
    guess = data["guess"]
    #guess = request.json["guess"]
    board = session["board"]
    result = boggle_game.check_valid_word(board, guess)
    return jsonify(result=result)

@app.route("/stats", methods=["POST"])
def update_stats():
    """
        Updates the user's high score and increments the number of times the
        user played.
    """
    data = request.get_json()
    score = data["score"]
    highscore = session.get("highscore", 0)
    highscore = highscore if highscore >= score else score
    session["highscore"] = highscore
    
    num_of_times_played = session.get("num_of_times_played", 0) + 1
    session["num_of_times_played"] = num_of_times_played
    return jsonify(num_of_times_played=num_of_times_played, \
        highscore=highscore)