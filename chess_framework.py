from stockfish import Stockfish
import chess
import chess.pgn
import chess.svg
import time
import io
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

from wand.api import library
import wand.color
import wand.image

def board_to_image(board):

    if board.turn == chess.BLACK:
        boardsvg = chess.svg.board(board=board, flipped=True)
    else:
        boardsvg = chess.svg.board(board=board)
    with open('board.svg','w') as f:
        f.write(boardsvg)

    with open('board.svg','r') as f:
        svg_str = f.read()
    svg_blob = svg_str.encode('utf-8')
    with wand.image.Image() as image:
        with wand.color.Color('transparent') as background_color:
            library.MagickSetBackgroundColor(image.wand, 
                                            background_color.resource) 
            
        image.read(blob=svg_blob)
        png_image = image.make_blob("png32")

    with open('board.png', "wb") as out:
        out.write(png_image)

def create_game(game_name, white,black):
    game = chess.pgn.Game()
    game.headers["Event"] = game_name
    game.headers['White'] = white
    game.headers['Black'] = black
    with open(f'{game_name}.txt','w') as f:
        f.write(str(game))
    board = game.board()
    board_to_image(board)
    return board    

def make_move(game_name, move):
    with open(f'{game_name}.txt','r') as f:
        game_str = f.read()
    pgn = io.StringIO(game_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    for i in game.mainline_moves():
        board.push(i)
    try:
        node = game.end()
        node = node.add_variation(board.parse_san(move))
        board.push(board.parse_san(move))
    except Exception as e:
        print(e)
        return False
    board_to_image(board)
    print(type(game))
    with open(f'{game_name}.txt','w') as f:
            f.write(str(game))
    
    if board.is_stalemate():
        print('Stalemate')
        return '1/2-1/2'
    elif board.is_insufficient_material():
        print('Stalemate by insufficient material')
        return '1/2-1/2'
    elif board.is_checkmate():
        R = board.outcome().result()
        if R == '1-0':
            print('White wins by checkmate')
        else:
            print('Black wins by checkmate')
        return R




def game(game_name, white,black, discord_bot=False):
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = game_name
    if discord_bot:
        watch = False

    
    print("White is "+white.name)
    print("Black is "+black.name)
    movecnt = 0

    while True:

        if board.is_stalemate():
            print('Stalemate')
            return '1/2-1/2'
        elif board.is_insufficient_material():
            print('Stalemate by insufficient material')
            return '1/2-1/2'
        elif board.is_checkmate():
            R = board.outcome().result()
            if R == '1-0':
                print('White wins by checkmate')
            else:
                print('Black wins by checkmate')
            return R
        
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
        
        with open(f'{game_name}.txt','w') as f:
            f.write(str(game))
        
        print('Turn: ', movecnt//2+1)
        movecnt += 1
        print(turn+' played: '+ board.san(move))
        board.push(move)
        board_to_image(board)
        if watch:
            time.sleep(0.5)
        
if __name__=='__main__':
    game("possessed vs human", human,possessed,watch=False)

