# Fun with Checkers
# Game tournament interface for the course CS 470/670 at UMass Boston
# Version 1.1 on 04/23/2020 by Marc Pomplun

import importlib
import numpy as np
import random as rnd
import time
from datetime import datetime
from graphics import *

playerModuleList = ['Alan_Turing', 'Cookie_Monster', 'Homer_Simpson','Raj_Mehta']
timeLimit = 2.0     # Limit for computer players' thinking time (seconds)
timeTolerance = 0.1
boardWidth = 6
boardHeight = 6
homeWidth = 2       
homeHeight = 2
squareSize = 100    # Size of each square (pixels)
textHeight = 50     # Height of the text display at the top of the window (pixels)
pieceColors = [color_rgb(50, 50, 250), color_rgb(230, 50, 50)]
squareColors = [color_rgb(100, 220, 100), color_rgb(110, 240, 110)]

class GameState(object):
    __slots__ = ['board', 'playerToMove', 'winner']

# Draw the board, pieces, and player names indicating active and winning players 
# If <currentMove>, show currently moving piece somewhere between its start position (moveProgress = 0)
# and its end position (moveProgress = 1) for move animation
def displayState(state, playerNames, selectedSquare, currentMove=None, moveProgress=0):
    win.delete('all')
    textPos = [boardWidth * squareSize / 4, boardWidth * squareSize * 3 / 4]
    for p in range(2):
        if state.winner == -1:
            if state.playerToMove == p: 
                t = Text(Point(textPos[p], textHeight / 2), '<< ' + playerNames[p] + ' >>')
            else:
                t = Text(Point(textPos[p], textHeight / 2), playerNames[p])
        else:
            if state.winner == p: 
                t = Text(Point(textPos[p], textHeight / 2), '!!! ' + playerNames[p] + ' !!!')
                t.setStyle("bold")
            else:
                t = Text(Point(textPos[p], textHeight / 2), playerNames[p])
        t.setFace("arial")
        t.setSize(min([int(textHeight / 3), 36]))
        t.setTextColor(pieceColors[p])            
        t.draw(win)

    # Show squares and pieces
    for x in range(boardWidth):
        for y in range(boardHeight):
            r = Rectangle(Point(squareSize * x, textHeight + squareSize * y), Point(squareSize * (x + 1), textHeight + squareSize * (y + 1)))
            if selectedSquare == (x, y):
                r.setFill("white")
            else:
                r.setFill(squareColors[(x + y) % 2])
            r.setWidth(0)
            r.draw(win)

            if state.board[x, y] >= 0 and (currentMove == None or currentMove[:2] != (x, y)):
                piece = Circle(Point(squareSize * x + squareSize / 2, squareSize * y + squareSize / 2 + textHeight), squareSize * 2 / 5)
                piece.setFill(pieceColors[state.board[x, y]])
                piece.setWidth(3)
                piece.draw(win)

    # Mark home areas
    l = Line(Point(squareSize * homeWidth, textHeight), Point(squareSize * homeWidth, textHeight + squareSize * homeHeight))
    l.setFill(pieceColors[0]);
    l.setWidth(3)
    l.draw(win)
    l = Line(Point(0, textHeight + squareSize * homeHeight), Point(squareSize * homeWidth, textHeight + squareSize * homeHeight))
    l.setFill(pieceColors[0]);
    l.setWidth(3)
    l.draw(win)
    l = Line(Point(squareSize * (boardWidth - homeWidth), textHeight + squareSize * boardHeight), 
             Point(squareSize * (boardWidth - homeWidth), textHeight + squareSize * (boardHeight - homeHeight)))
    l.setFill(pieceColors[1]);
    l.setWidth(3)
    l.draw(win)
    l = Line(Point(squareSize * boardWidth, textHeight + squareSize * (boardHeight - homeHeight)), 
             Point(squareSize * (boardWidth - homeWidth), textHeight + squareSize * (boardHeight - homeHeight)))
    l.setFill(pieceColors[1]);
    l.setWidth(3)

    # Show moving piece somewhere between its start and end points (moveProgress between 0 and 1)
    if currentMove != None:
        x = moveProgress * (currentMove[2] - currentMove[0]) + currentMove[0]
        y = moveProgress * (currentMove[3] - currentMove[1]) + currentMove[1]
        movingPiece = Circle(Point(squareSize * x + squareSize / 2, squareSize * y + squareSize / 2 + textHeight), squareSize * 2 / 5)
        movingPiece.setFill(pieceColors[state.playerToMove])
        movingPiece.setWidth(3)
        movingPiece.draw(win)

    l.draw(win)

    if currentMove == None:
        update()
    else:
        update(30)

# Get coordinates of the square selected by the human player
def getClickedSquare():
    while True:
        clickPos = win.getMouse()
        squareX = int(clickPos.x / squareSize)
        squareY = int((clickPos.y - textHeight) / squareSize)
        if squareX >= 0 and squareX < boardWidth and squareY >= 0 and squareY < boardHeight:
            return (squareX, squareY)

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

# Compute the winner's points, which is the number of individual moves (non-jumps) that the losing player would need
# to place all of their remining pieces in the winner's home area 
def getPoints(state):
    points = 0
    for x in range(boardWidth):                             # Search board for losing player's pieces
        for y in range(boardHeight):
            if state.board[x, y] == 1 - state.winner:
                if state.winner == 0:                       # Add the number of moves (non-jumps) to reach the home area to <points>
                    points += max([0, x - homeWidth + 1]) + max([0, y - homeHeight + 1])
                else:
                    points += max([0, boardWidth - homeWidth - x]) + max([0, boardHeight - homeHeight - y])
    return points

# Play a game with players indicated by their indices in playerList. Human player is indicated by index == None. 
# Return the points for each player (winner: move advantage over opponent; loser: 0) 
def playGame(indexPlayer1, indexPlayer2):
    # Get player names and type (human vs. computer)
    moduleIndices = [indexPlayer1, indexPlayer2]
    playerNames = []
    isHuman = []

    if indexPlayer1 == None:
        playerNames.append('Human Player')
        isHuman.append(True)
    else:
        playerNames.append(playerModuleList[indexPlayer1])
        isHuman.append(False)
    
    if indexPlayer2 == None:
        playerNames.append('Human Player')
        isHuman.append(True)
    else:
        playerNames.append(playerModuleList[indexPlayer2])
        isHuman.append(False)

    state = GameState()     # Create initial game state
    state.board = -np.ones((boardWidth, boardHeight), dtype=int)
    state.board[:homeWidth, :homeHeight] = 0
    state.board[-homeWidth:, -homeHeight:] = 1
    state.playerToMove = 0
    state.winner = -1
    displayState(state, playerNames, None)

    if not isHuman[0]:      # Brief delay to show the initial game state before a computer's first move
        time.sleep(1)

    while state.winner < 0:
        displayState(state, playerNames, None)
        moveList = getMoveOptions(state)
        if not moveList:
            state.winner = state.playerToMove
            (xStart, yStart) = (-1, -1)
            break

        if isHuman[state.playerToMove]:                  # Human player
            repeatEntry = True
            while repeatEntry:                              
                displayState(state, playerNames, None)
                legalStart = False                       # Get start position for human's move
                while not legalStart:                    
                    (xStart, yStart) = getClickedSquare()
                    for (xS, yS, _, _) in moveList:
                        if (xS, yS) == (xStart, yStart):
                            legalStart = True
                            break

                displayState(state, playerNames, (xStart, yStart))
                legalEnd = False                         # Get end position for human's move
                while not legalEnd: 
                    (xEnd, yEnd) = getClickedSquare()
                    for move in moveList:
                        if move == (xStart, yStart, xEnd, yEnd):
                            legalEnd = True
                            repeatEntry = False
                            break
                    if (xStart, yStart) == (xEnd, yEnd):
                        legalEnd = True
            move = (xStart, yStart, xEnd, yEnd)
        else:                                            # Computer player
            startTime = datetime.now()
            move = players[moduleIndices[state.playerToMove]].getMove(state, homeWidth, homeHeight, timeLimit)
            duration = datetime.now() - startTime
            if duration.seconds + duration.microseconds * 1e-6 >= timeLimit + timeTolerance:
                print("Time violation by player " + playerNames[state.playerToMove])
                move = moveList[0]              # If computatiomn took too long or illegal move is returned, just pick first move from list
            else:
                if not (move in moveList):
                    print("Illegal move by player " + playerNames[state.playerToMove])
                    move = moveList[0]
    
        for i in range(1, 15):
            displayState(state, playerNames, None, move, i / 14)
        
        state = makeMove(state, move) 
        displayState(state, playerNames, None)
    
    if state.winner == 0:
        return (getPoints(state), 0)
    return (0, getPoints(state))

# Play a game by picking computer players by their index in <players> or putting <None> for a human player
def singleGame(indexPlayer1, indexPlayer2):
    if indexPlayer1 == None:
        player1Name = 'Human Player'
    else:
        player1Name = playerModuleList[indexPlayer1]
    
    if indexPlayer2 == None:
        player2Name = 'Human Player'
    else:
        player2Name = playerModuleList[indexPlayer2]

    (points1, points2) = playGame(indexPlayer1, indexPlayer2)   
    print(player1Name + ' vs. ' + player2Name + ' ' + str(points1) + ' - ' + str(points2))

    time.sleep(2)
    return (points1, points2)

# Play a round-robin computer player tournament in which any two players compete against each other twice (to play each side once)
# Afterwards, rank players by number of victories. If victories are identical, rank by number of points.
def computerTournament(playerIndexList):
    gameList = []
    for player1 in range(len(playerIndexList)):
        for player2 in range(len(playerIndexList)):
            if player1 != player2:
                gameList.append((player1, player2))

    rnd.shuffle(gameList)
    victories = np.zeros(len(playerIndexList), dtype=int) 
    points = np.zeros(len(playerIndexList), dtype=int)

    for (player1, player2) in gameList:
        (points1, points2) = singleGame(playerIndexList[player1], playerIndexList[player2])
        points[player1] += points1
        points[player2] += points2
        if points1 > points2:
            victories[player1] += 1
        else:
            victories[player2] += 1
    
    rankingScore = 1e6 * victories + points
    ranking = np.argsort(rankingScore)

    print('\nFinal Standings:\n')
    print('Name                          Victories Points\n')

    for r in ranking[::-1]:
        name = playerModuleList[playerIndexList[r]]
        spaces = ' ' * (30 - len(name))
        print(name + spaces + str(victories[r]) + '\t\t' + str(points[r]))

    print('')

# Main script
win = GraphWin("Fun with Checkers", boardWidth * squareSize, textHeight + boardHeight * squareSize, autoflush=False)
win.setBackground("black")

players = []        # Import player modules
for player in playerModuleList:
    players.append(importlib.import_module(player))

computerTournament([0,3])

#singleGame(2, None)

win.close()

