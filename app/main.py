from flask import Blueprint, render_template, session, redirect, abort, request
# from flask_socketio import SocketIO, emit, join_room, leave_room
import pusher
import json

from . import Game

main = Blueprint("main", __name__)

games = {}

pusher_client = pusher.Pusher(
    app_id='1601367',
    key='27a9c27858a52b91a94e',
    secret='87372078321279e2f0e0',
    cluster='eu',
    ssl=True
)

@main.route("/")
def index():
    return render_template("index.html", existing_games=list(games.keys()))

@main.route("/delete_game/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    pusher_client.trigger(f"game{game_id}", "kick", None)
    if not games.pop(game_id, False):
        abort(404, f"Game {game_id} not found")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route("/play/<int:game_id>")
def play(game_id):
    game = games.setdefault(game_id, Game())
    session["game_id"] = game_id
    return render_template("play.html")

@main.route("/play")
def create_game():
    game_id = 1
    while game_id in games:
        game_id += 1
    return redirect(f"/play/{game_id}")

@main.route("/pusher/auth", methods=['POST'])
def pusher_authentication():
    session["socket_id"] = request.form["socket_id"]
    auth = pusher.authenticate(channel=request.form['channel_name'],socket_id=request.form['socket_id'])
    return json.dumps(auth)

@main.route("/role", methods=["POST"])
def get_role():
    game_id = session["game_id"]
    game: Game = games[game_id]
    socket_id = request.data
    session["socket_id"] = socket_id

    if game.white_socket_id is None:
        game.white_socket_id = socket_id
        role = "w"
    elif game.black_socket_id is None:
        game.black_socket_id = socket_id
        role = "b"
    else:
        role = "s"
    
    emit_board(f"game{game_id}", game.fen(), game.can_veto)

    return {'role': role}

@main.route("/disconnect", methods=["POST"])
def disconnect():
    game: Game = games[session["game_id"]]
    if game.white_socket_id == session["socket_id"]:
        game.white_socket_id = None
    elif game.black_socket_id == session["socket_id"]:
        game.black_socket_id = None
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route("/move", methods=["POST"])
def move():
    game: Game = games[session["game_id"]]
    uci = request.json["uci"]
    game.make_move(uci)
    emit_board(f"game{session['game_id']}", game.fen(), game.can_veto)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route("/veto", methods=["POST"])
def veto():
    game: Game = games[session["game_id"]]
    source, target = game.veto()
    emit_board(f"game{session['game_id']}", game.fen(), game.can_veto, banned_source=source, banned_target=target)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route("/new_game", methods=["POST"])
def restart_game():
    game: Game = games[session["game_id"]]
    game.reset()
    emit_board(f"game{session['game_id']}", game.fen(), game.can_veto)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def emit_board(channel: str, fen: str, can_veto: bool, **kwargs):
    pusher_client.trigger(channel, "update_board", {"fen": fen, "can_veto": can_veto, **kwargs})
