# Player Raj_Mehta

import random as rnd
import numpy as np
from datetime import datetime,timedelta
import importlib
import numpy as np
import random as rnd
import time
from datetime import datetime
from graphics import *

class GameState(object):
    __slots__ = ['board', 'playerToMove', 'winner']

# Global variables
boardWidth = 0
boardHeight = 0
homeWidth = 0
homeHeight = 0
timeLimit = 0

# Compute list of legal moves for a given GameState for the player moving next 
def getMoveOptions(state):
    direction = [[(1, 0), (0, 1)], [(-1, 0), (0, -1)]]              # Possible (dx, dy) moving directions for each player
    moves = []
    for xStart in range(boardWidth):                                # Search board for player's pieces
        for yStart in range(boardHeight):
            if state.board[xStart, yStart] == state.playerToMove:   # Found a piece!
                for (dx, dy) in direction[state.playerToMove]:      # Check horizontal and vertical moving directions
                    (xEnd, yEnd) = (xStart + dx, yStart + dy)
                    while xEnd >= 0 and xEnd < boardWidth and yEnd >= 0 and yEnd < boardHeight:
                        if state.board[xEnd, yEnd] == -1:
                            moves.append((xStart, yStart, xEnd, yEnd))      # If square is free, we have a legal move...
                            break
                        xEnd += dx                                          # Otherwise, check for larger step
                        yEnd += dy
    return moves

# For a given GameState and move to be executed, return the GameState that results from the move
def makeMove(state, move):
    (xStart, yStart, xEnd, yEnd) = move
    newState = GameState()

    newState.playerToMove = 1 - state.playerToMove          # After the move, it's the other player's turn
    newState.board = np.copy(state.board)
    newState.board[xStart, yStart] = -1                     # Remove the piece at the start position
    if (state.playerToMove == 0 and (xEnd < boardWidth - homeWidth or yEnd < boardHeight - homeHeight)) or \
       (state.playerToMove == 1 and (xEnd >= homeWidth or yEnd >= homeHeight)):
        newState.board[xEnd, yEnd] = state.playerToMove     # Unless the move ends in the opponent's home, place piece at end position
    
    for xStart in range(boardWidth):
        for yStart in range(boardHeight):
            if newState.board[xStart, yStart] == state.playerToMove:
                newState.winner = -1                        # If the player still has pieces on the board, then there is no winner yet...
                return newState
    
    newState.winner = state.playerToMove                    # Otherwise, the current player has won!
    return newState

# Return the evaluation score for a given GameState; higher score indicates a better situation for Player 1
# Alan_Turing's evaluation function is based on the (non-jump) moves each player would need to win the game. 
def getScore(state):
    score = 0
    for x in range(boardWidth):                             # Search board for any pieces
        for y in range(boardHeight):
            if state.board[x, y] == 0:                      # Subtract the number of moves (non-jumps) for Player 1's piece to reach Player 2's home area
                score -= max([0, boardWidth - homeWidth - x]) + max([0, boardHeight - homeHeight - y])
            else:
                if state.board[x, y] == 1:                  # Add the number of moves (non-jumps) for Player 2's piece to reach Player 1's home area
                    score += max([0, x - homeWidth + 1]) + max([0, y - homeHeight + 1])
    return score

# Check whether time limit has been reached
def timeOut(startTime, timeLimit):
    duration = datetime.now() - startTime
    return duration.seconds + duration.microseconds * 1e-6 >= timeLimit

# Compute the next move to be played; keep updating <bestMoveSoFar> until computation finished or time limit reached
def isGameOver(state):
    print(state)
    if state.winner == -1:
       print('Nobody has won yet')
       return -1
    if state.winner == 0:
       print('Player 1 has won')
       return 0
    if state.winner == 1:
       print('Player 2 has won')
       return 1
def MinMax(state, playerToMove,depth,maxDepth):    
   if ( isGameOver(state) == 0 or isGameOver(state) == 1 or depth == maxDepth ):     
      return getScore(state)  
   
   
   
   if ( state.playerToMove == 0 ):                                             
      score = float('-inf')  
   else:
      score = float('inf')                                                       
   MoveList= getMoveOptions(state)                                 # Get the list of possible moves
                                        # Just choose first move from the list for now, in case we run out of time
  
   for move in MoveList: 
      projectedState = makeMove(state, move)
      score = MinMax(projectedState, playerToMove, depth+1, maxDepth)       
      if ( state.playerToMove == 0 ):          
         if ( score > bestScore ):  
            bestScore = score 
            bestMoveSoFar = move            
      else:        
         if ( score < bestScore ):  
            bestScore = score 
            bestMoveSoFar = move
            
   return bestScore, bestMoveSoFar

def getMove(state, hWidth, hHeight, timeLimit):
    # Set global variables
    startTime = datetime.now()
    
    # state = GameState()
    # state.board = globalState.board.copy()
    # state.playerToMove = globalState.playerToMove
    # state.winner = globalState.winner
    # state.homeWidth = hWidth
    # state.homeHeight = hHeight  
    
    global boardWidth, boardHeight, homeWidth, homeHeight
    boardWidth = state.board.shape[0]
    boardHeight = state.board.shape[1]
    homeWidth = hWidth
    homeHeight = hHeight
    #state = GameState()
    safetyMovesList= getMoveOptions(state)                                 # Get the list of possible moves
    bestMoveSoFar = safetyMovesList[0]                                     # Just choose first move from the list for now, in case we run out of time
    maxDepth = 4
    
    while maxDepth < 20:
   
      nextMove = MinMax(state,maxDepth,startTime, timeLimit)
      if nextMove[0] == -1:
          print('Timeout!')
          break
      else:
          duration = datetime.now() - startTime
          print('Depth %d completed after %.4f seconds'%(maxDepth,duration.seconds + duration.microseconds * 1e-6))
          bestMoveSoFar = nextMove
      maxDepth += 1
    
    return tuple(bestMoveSoFar)    