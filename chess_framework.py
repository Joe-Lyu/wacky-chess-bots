from stockfish import Stockfish
import chess
import chess.pgn
from chessboard import display
import time
import cairosvg
from PIL import Image
stockfish = Stockfish(path="./stockfish/stockfish-windows-x86-64-avx2.exe")

from players import sf_move, wf_move, di_move, dq_move, possessed_move, manual_move
class ChessPlayer():
    def __init__(self,name,engine):
        self.name = name
        self.engine = engine
        self.last_move = None
    def get_move(self,board):
        return self.engine(self, board)



sf = ChessPlayer('Stockfish',sf_move)
human = ChessPlayer('Human',manual_move)
drawish = ChessPlayer('Drawish',di_move)
worstfish = ChessPlayer('Worstfish',wf_move)
dramaqueen = ChessPlayer('DramaQueen',dq_move)
possessed = ChessPlayer('Possessed',possessed_move)

def game(game_name, white,black,watch=False):
    board = chess.Board()

    game = chess.pgn.Game()
    game.headers["Event"] = game_name

    if watch:
        game_board = display.start()
        if black.name == 'Human':
            display.flip(game_board)
    
    print("White is "+white.name)
    print("Black is "+black.name)
    movecnt = 0

    while True:
        position = board.fen()

        if board.is_stalemate():
            print('Stalemate')
            display.terminate()
            return '1/2-1/2'
        elif board.is_insufficient_material():
            print('Stalemate by insufficient material')
            display.terminate()
            return '1/2-1/2'
        elif board.is_checkmate():
            R = board.outcome().result()
            if R == '1-0':
                print('White wins by checkmate')
            else:
                print('Black wins by checkmate')
            display.terminate()
            return R
        if watch:
            display.update(position, game_board)
            display.check_for_quit()

        turn = 'White' if movecnt % 2 == 0 else 'Black'

        if turn == 'White':
            move = white.get_move(board)
            white.last_move = move
        else:
            move = black.get_move(board)
            black.last_move = move

        if movecnt == 0:
            node = game.add_variation(move)
        else:
            node = node.add_variation(move)
        
        with open('game.txt','w') as f:
            f.write(str(game))
        
        print('Turn: ', movecnt//2+1)
        movecnt += 1
        print(turn+' played: '+ board.san(move))
        board.push(move)
        # print('Position:')
        # print(board)
        board_vis = Image.open(cairosvg.svg2png(file_obj=chess.svg.board(board)))
        board_vis.show()
        if watch:
            time.sleep(0.5)
        
if __name__=='__main__':
    game("possessed vs human", human,possessed,watch=False)

