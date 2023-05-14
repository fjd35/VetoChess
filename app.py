from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room

from board import Board

app = Flask(__name__)
app.config["SECRET_KEY"] = "reallyreallysecret"
socketio = SocketIO(app)

games = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play/<int:game_id>")
def play(game_id):
    global games
    game = games.setdefault(game_id, Board())
    session["game_id"] = game_id
    return render_template("play.html")

@socketio.on("joined")
def joined(socket_id):
    global games
    game: Board = games[session["game_id"]]
    session["socket_id"] = socket_id
    join_room(session["game_id"])

    if game.white_socket_id is None:
        game.white_socket_id = socket_id
        emit("role", "w") # white
    elif game.black_socket_id is None:
        game.black_socket_id = socket_id
        emit("role", "b") # black
    else:
        emit("role", "s") # spectator
    
    emit("update_board", {"pgn": game.board_state, "can_veto": True}, to=session["game_id"])

@socketio.on("disconnect")
def disconnect():
    print(f"{session['socket_id']} left")
    global games
    game: Board = games[session["game_id"]]
    if game.white_socket_id == session["socket_id"]:
        game.white_socket_id = None
    elif game.black_socket_id == session["socket_id"]:
        game.black_socket_id = None
    leave_room(session["game_id"])

@socketio.on("move")
def move(new_board_state: str):
    global games
    game: Board = games[session["game_id"]]
    game.update_board_state(new_board_state)
    emit("update_board", {"pgn": game.board_state, "can_veto": True}, to=session["game_id"])

@socketio.on("veto")
def veto():
    global games
    game: Board = games[session["game_id"]]
    game.veto()
    emit("update_board", {"pgn": game.board_state, "can_veto": False}, to=session["game_id"])

if __name__ == "__main__":
    socketio.run(app, debug=True)