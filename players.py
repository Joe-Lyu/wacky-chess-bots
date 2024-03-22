from stockfish import Stockfish
import chess
import chess.pgn
stockfish = Stockfish(path="./stockfish/stockfish-windows-x86-64-avx2.exe")

def manual_move(self, board):
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

def sf_move(self, board):
    position = board.fen()
    stockfish.set_fen_position(position)
    return chess.Move.from_uci(stockfish.get_best_move())

def wf_move(self, board):
    position = board.fen()
    stockfish.set_fen_position(position)
    all_sf_moves = stockfish.get_top_moves(220)
    return chess.Move.from_uci(all_sf_moves[-1]['Move']) # worst move

def di_move(self, board):
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


def dq_move(self, board):
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
        
def possessed_move(self,board):
    position = board.fen()
    stockfish.set_fen_position(position)
    all_sf_moves = stockfish.get_top_moves(220)
    if self.last_move is not None:
        last_move = self.last_move.uci()
        possessed_piece_coords = last_move[2:4]
        for move in all_sf_moves:
            if move['Move'][0:2] == possessed_piece_coords:
                return chess.Move.from_uci(move['Move'])
        return chess.Move.from_uci(stockfish.get_best_move())
    else:
        return chess.Move.from_uci(stockfish.get_best_move())