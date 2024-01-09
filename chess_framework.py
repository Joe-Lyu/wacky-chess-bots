from stockfish import Stockfish
import chess
import chess.pgn
from chessboard import display
import time
stockfish = Stockfish(path="./stockfish/stockfish-windows-x86-64-avx2.exe")

class ChessPlayer():
    def __init__(self,name,engine):
        self.name = name
        self.engine = engine
    def get_move(self,board):
        return self.engine(board)

def sf_move(board):
    position = board.fen()
    stockfish.set_fen_position(position)
    return chess.Move.from_uci(stockfish.get_best_move())

def wf_move(board):
    position = board.fen()
    stockfish.set_fen_position(position)
    all_sf_moves = stockfish.get_top_moves(220)
    return chess.Move.from_uci(all_sf_moves[-1]['Move']) # worst move

def di_move(board):
    position = board.fen()
    stockfish.set_fen_position(position)
    side = 1 if 'w' in position else -1
    all_sf_moves = stockfish.get_top_moves(220)
    ev = stockfish.get_evaluation()

    if ev['type'] == 'mate' and ev['value']*side > 0: # checkmate imminent (winning)
        for i in range(len(all_sf_moves)):
            if all_sf_moves[i]['Mate'] is None:
                return chess.Move.from_uci(all_sf_moves[i]['Move']) # best non-checkmate move
        return chess.Move.from_uci(all_sf_moves[-1]['Move']) # worst checkmate move

    elif ev['type'] == 'mate' and ev['value']*side <= 0: # checkmate imminent (losing)
        return chess.Move.from_uci(stockfish.get_best_move())


    for i in range(len(all_sf_moves)-1):
        if all_sf_moves[i]['Mate'] is not None:
            continue
        if all_sf_moves[i]['Centipawn'] * all_sf_moves[i+1]['Centipawn'] < 0: # worst advantageous move (stalemate-inducing i hope)
            return chess.Move.from_uci(all_sf_moves[i]['Move'])

    if ev['value'] * side < 0: # losing very hard
        return chess.Move.from_uci(all_sf_moves[0]['Move'])
    
    else:
        return chess.Move.from_uci(all_sf_moves[-1]['Move'])

def manual_move(board):
    legalmoves =  board.legal_moves
    while True:
        move = input("Enter a valid move: \n")
        try:
            if not board.parse_san(move) in legalmoves:
                print('Illegal move, try again')
                continue
        except:
            print("Invalid move, try again")
            continue
        break
        
    return board.parse_san(move)

def dq_move(board):
    position = board.fen()
    stockfish.set_fen_position(position)
    all_sf_moves = stockfish.get_top_moves(220)
    best,worst = all_sf_moves[0], all_sf_moves[-1]
    if best['Mate'] is not None and worst['Mate'] is not None: # if both sides have imminent checkmate
        if best['Mate'] < worst['Mate']:
            return chess.Move.from_uci(best['Move'])
        return chess.Move.from_uci(worst['Move'])
    
    elif best['Mate'] is not None: # checkmate is more dramatic than non-checkmate
        return chess.Move.from_uci(best['Move'])
    elif worst['Mate'] is not None: 
        return chess.Move.from_uci(worst['Move'])
    
    else: # no checkmate
        if abs(best['Centipawn']) > abs(worst['Centipawn']):
            return chess.Move.from_uci(best['Move'])
        else:
            return chess.Move.from_uci(worst['Move']) # always pick the most dramatic move


sf = ChessPlayer('Stockfish',sf_move)
human = ChessPlayer('Human',manual_move)
drawish = ChessPlayer('Drawish',di_move)
worstfish = ChessPlayer('Worstfish',wf_move)
dramaqueen = ChessPlayer('DramaQueen',dq_move)


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
        else:
            move = black.get_move(board)

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
        
        if watch:
            time.sleep(0.5)
        
if __name__=='__main__':
    game("Drama queen vs me", dramaqueen,human,watch=True)

