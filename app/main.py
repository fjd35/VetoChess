from flask import Blueprint, render_template, session, redirect, abort
from flask_socketio import SocketIO, emit, join_room, leave_room
import json

from . import socketio, Game

main_blueprint = Blueprint("main_blueprint", __name__)

games = {}

@main_blueprint.route("/")
def index():
    return render_template("index.html", existing_games=list(games.keys()))

@main_blueprint.route("/delete_game/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    emit("kick", to=game_id, namespace="/")
    if not games.pop(game_id, False):
        abort(404, f"Game {game_id} not found")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main_blueprint.route("/play/<int:game_id>")
def play(game_id):
    game = games.setdefault(game_id, Game())
    session["game_id"] = game_id
    return render_template("play.html")

@main_blueprint.route("/play")
def new_game():
    game_id = 1
    while game_id in games:
        game_id += 1
    return redirect(f"/play/{game_id}")

@socketio.on("joined")
def joined(socket_id):
    game: Game = games[session["game_id"]]
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
    
    emit_board(game.fen(), game.can_veto)

@socketio.on("disconnect")
def disconnect():
    print(f"{session['socket_id']} left")
    game: Game = games[session["game_id"]]
    if game.white_socket_id == session["socket_id"]:
        game.white_socket_id = None
    elif game.black_socket_id == session["socket_id"]:
        game.black_socket_id = None
    leave_room(session["game_id"])

@socketio.on("move")
def move(uci):
    game: Game = games[session["game_id"]]
    game.make_move(uci)
    emit_board(game.fen(), game.can_veto)

@socketio.on("veto")
def veto():
    game: Game = games[session["game_id"]]
    source, target = game.veto()
    print(game.fen())
    emit_board(game.fen(), game.can_veto, banned_source=source, banned_target=target)

@socketio.on("new_game")
def new_game():
    game: Game = games[session["game_id"]]
    game.reset()
    emit_board(game.fen(), game.can_veto)

def emit_board(fen: str, can_veto: bool, **kwargs):
    emit("update_board", {"fen": fen, "can_veto": can_veto, **kwargs}, to=session["game_id"])
