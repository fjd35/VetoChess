

class Board:
    def __init__(self, white_socket_id: str=None, black_socket_id: str=None, board_state: str=None):
        if board_state is None:
            board_state = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        self.white_socket_id = white_socket_id
        self.black_socket_id = black_socket_id
        self.board_state = board_state
        self.previous_board_state = None
    
    def __repr__(self):
        return (f"Board("
            f"white_socket_id: {self.white_socket_id}, "
            f"black_socket_id: {self.black_socket_id}, "
            f"board_state: {self.board_state}, "
            f"previous_board_state: {self.previous_board_state})"
        )

    def update_board_state(self, board_state):
        self.previous_board_state = self.board_state
        self.board_state = board_state

    def veto(self):
        self.board_state = self.previous_board_state
        self.previous_board_state = None
