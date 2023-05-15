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
var banned_source = null;
var banned_target = null;


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
    if (move === null) {
        console.log('illegal')
        return 'snapback'
    } 
    if (source === banned_source && target === banned_target) {
        console.log('banned')
        game.undo()
        return 'snapback'
    }

    prev_move = move;
    banned_source = null;
    banned_target = null;
    socket.emit('move', source + target + (move.promotion || ''));

    updateStatus()
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen());
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
    socket.emit('veto');
}

function new_game () {
    socket.emit("new_game");
}

socket.on('connect', function() {
    socket.emit('joined', socket.id);
    console.log('joined');
});
socket.on('role', function(data) {
    role = data;

    board.orientation((role === 'b') ? 'black' : 'white');
    
    var full_role;
    switch(role) {
        case 'w':
            full_role = 'White';
            break;
        case 'b':
            full_role = 'Black';
            break
        default:
            full_role = 'Spectator';
    }
    $('#role').html(full_role);
});
socket.on('update_board', function(data) {
    game.load(data['fen']);
    board.position(game.fen());
    can_veto = data['can_veto'];
    if ('banned_source' in data) {
        banned_source = data['banned_source'];
        banned_target = data['banned_target'];
    }
    updateStatus()
});
socket.on('kick', function() {
    window.location.replace("/");
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
$('#newGameBtn').on('click', new_game);
