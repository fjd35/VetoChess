var board = null
var game = new Chess()

function makeRandomMove () {
    if (game.game_over()) {
        return
    }
  
    var possibleMoves = game.moves()

    var randomIdx = Math.floor(Math.random() * possibleMoves.length)
    game.move(possibleMoves[randomIdx])
    board.position(game.fen())

    window.setTimeout(makeRandomMove, 500)
}

function deleteGame(game_id) {
    fetch('/delete_game/' + game_id,  {
        method: 'DELETE'
    }).then((response) => {
        window.location.reload();
    })
}

window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted || 
                           ( typeof window.performance != "undefined" && 
                                window.performance.navigation.type === 2 );
    if ( historyTraversal ) {
      // Handle page restore.
      window.location.reload();
    }
});

board = Chessboard('myBoard', 'start')

window.setTimeout(makeRandomMove, 500)