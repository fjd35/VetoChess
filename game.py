import chess
import chess.pgn

class Game(chess.Board):
    def __init__(
            self, white_socket_id: str=None,
            black_socket_id: str=None,
            starting_fen: str=chess.STARTING_FEN
        ):
        
        super().__init__(fen=starting_fen)

        self.white_socket_id = white_socket_id
        self.black_socket_id = black_socket_id
        self.banned_move = None
        self.can_veto = False
    
    def __repr__(self):
        return (f"Board("
            f"white_socket_id: {self.white_socket_id}, "
            f"black_socket_id: {self.black_socket_id}, "
            f"fen: {self.fen()}, "
            f"banned_move: {self.banned_move}, "
            f"can_veto: {self.can_veto})"
        )

    def veto(self):
        move = self.pop()
        self.banned_move = move
        self.can_veto = False
        return chess.SQUARE_NAMES[move.from_square], chess.SQUARE_NAMES[move.to_square]

    def make_move(self, uci):
        move = chess.Move.from_uci(uci)
        if move in self.legal_moves and move != self.banned_move:
            self.push(move)
            if self.banned_move is None:
                self.can_veto = True
            self.banned_move = None
            return True
        return False

    def reset(self):
        super(Game, self).reset()
        self.banned_move = None
        self.can_veto = False

