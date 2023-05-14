var board = null
var game = new Chess()
var $status = $('#status')
var $fen = $('#fen')
var $pgn = $('#pgn')
var $vetoBtn = $('#vetoBtn')
var socket = io();
var role;
var can_veto = true;
var prev_move;
var banned_move = null;


function onDragStart (source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false

    // only pick up pieces for the side to move
    re = new RegExp('^' + role);
    if (game.turn() !== role || piece.search(re) === -1) {
        return false
    }
}

function onDrop (source, target) {
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })

    // illegal move
    if (move === null || move === banned_move) return 'snapback'

    prev_move = move;
    banned_move = null;

    updateStatus()
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen());
    socket.emit('move', game.pgn());
}

function updateStatus () {
    var status = ''

    var moveColor = 'White'
    if (game.turn() === 'b') {
        moveColor = 'Black'
    }

    // checkmate?
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.'
    }

    // draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position'
    }

    // game still on
    else {
        status = moveColor + ' to move'

        // check?
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check'
        }
    }

    $status.html(status)
    $fen.html(game.fen())
    $pgn.html(game.pgn())
    $vetoBtn.prop('disabled', !(can_veto && game.turn() === role))
}

function veto () {
    banned_move = prev_move;
    socket.emit('veto');
}

socket.on('connect', function() {
    socket.emit('joined', socket.id);
    console.log('joined');
});
socket.on('role', function(data) {
    role = data;
    console.log('role: ' + role)
    board.orientation((role === 'b') ? 'black' : 'white');
});
socket.on('update_board', function(data) {
    game.load_pgn(data['pgn']);
    board.position(game.fen());
    can_veto = data['can_veto'];
    updateStatus()
})

var config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)

updateStatus()


$vetoBtn.on('click', veto);
