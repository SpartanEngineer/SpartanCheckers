import copy, random, tkFont, time
from Tkinter import *
from functools import partial
 
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#Author: Donovan Miller
#Date: 01/29/17
#Description: This code uses machine learning to train a tic tac toe game AI.  
#   It also includes code to allow playing against the trained AI via a Tkinter
#   GUI.
#-------------------------------------------------------------------------------------
#Run via Python 2.7
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

#the board is a list of size 9 that contains information about the current tic
#   tac toe board
#the board maps as follows:
#   0 == top left space
#   1 == top center space
#   2 == top right space
#   3 == center left space
#   4 == center center space
#   5 == center right space
#   6 == bottom left space
#   7 == bottom center space
#   8 == bottom right space
#value mapping for a space in each board:
#   0 == empty space
#   1 == x space
#   2 == o space

learnConstant = 0.1 # learning constant

def getCheckLists(board):
    b = []
    b.append(board[0:3]) #horizontal
    b.append(board[3:6])
    b.append(board[6:9])
    b.append([board[y] for y in range(9) if(y == 0 or y == 3 or y == 6)]) #vertical
    b.append([board[y] for y in range(9) if(y == 1 or y == 4 or y == 7)])
    b.append([board[y] for y in range(9) if(y == 2 or y == 5 or y == 8)])
    b.append([board[y] for y in range(9) if(y == 0 or y == 4 or y == 8)]) #diagonal
    b.append([board[y] for y in range(9) if(y == 2 or y == 4 or y == 6)])
    return b

#true if there is three in a row, false if not
#x parameter should be 1(x) or 2(o)
def threeInARow(board, x, a=[]):
    if(a == []):
        a = getCheckLists(board)

    for c in a:
        if(c.count(x) == 3):
            return True

    return False

#returns the # of places where there is 2 x/o's & an empty space in a row/col/diagonal
def twoInARow(board, x, a=[]):
    result = 0
    if(a == []):
        a = getCheckLists(board)

    for c in a:
        if(c.count(x) == 2 and c.count(0) == 1):
            result += 1

    return result 

#returns the # of places where there is an x/o and 2 empty spaces in a row/col/diagonal
def openOne(board, x, a=[]):
    result = 0
    if(a == []):
        a = getCheckLists(board)

    for c in a:
        if(c.count(x) == 1 and c.count(0) == 2):
            result += 1

    return result

#this function determines if the game is: ongoing, a draw, a win for x, a win for o
def getGameState(board):
    checkLists = getCheckLists(board)
    if(threeInARow(board, 1, checkLists)):
        return 1 #x win
    elif(threeInARow(board, 2, checkLists)):
        return 2 #o win
    elif(board.count(0) != 0):
        return 3 #game still going
    else:
        return 0 #draw

conv = {True:1, False:0}
#returns a list of the features used to evaluate the value of a tic tac toeboard
#the features are as follows:
#   is there 3 x's in a row (0 or 1)
#   is there 3 o's in a row (0 or 1)
#   # of places where there is 2 x's beside an empty space
#   # of places where there is 2 o's beside an empty space
#   # of places where there is an x and two empty spaces in a row/col/diagonal
#   # of places where there is an o and two empty spaces in a row/col/diagonal
def getFeatures(board):
    a = board
    checkLists = getCheckLists(a)
    return [conv[threeInARow(a, 1, checkLists)], 
            conv[threeInARow(a, 2, checkLists)],
            twoInARow(a, 1, checkLists),
            twoInARow(a, 2, checkLists),
            openOne(a, 1, checkLists),
            openOne(a, 2, checkLists)]

#returns the value of a board based on the features (of the board) and their respective weights
def estimateMoveValue(features, weights):
    result = 0
    for i in range(len(features)):
        result += (features[i] * weights[i])
    return result 

#makes the best possible amongst all of the possible moves
def makeBestMove(board, weights, x):
    boards, values = [], [] 
    positions = [i for i in range(9) if(board[i] == 0)]
    for i in range(len(positions)):
        position = positions[i]
        newBoard = copy.deepcopy(board)
        newBoard[position] = x

        features = getFeatures(newBoard)
        value = estimateMoveValue(features, weights)

        boards.append(newBoard)
        values.append(value)
        
    mValue = values[0]
    mPosition = positions[0] 
    for i in range(1, len(positions)):
        if(values[i] > mValue):
            mValue = values[i]
            mPosition = positions[i] 

    board[mPosition] = x

#makes a random move
def makeRandomMove(board, x):
    a = [i for i in range(9) if(board[i] == 0)]
    randomNum = random.randint(0, len(a)-1)
    board[a[randomNum]] = x

#plays a tic-tac-toe game between the X and O AI
#we pit AI's against each other in order to train our AI's 
def playGame(xWeights, oWeights, xTrain, oTrain):
    turn = 1 
    board = [0 for x in range(9)]
    gameState = 3
    while(gameState == 3):
        if(turn == 1):
            makeBestMove(board, xWeights, turn)
            xTrain.append(copy.deepcopy(board))
        else:
            makeBestMove(board, oWeights, turn)
            oTrain.append(copy.deepcopy(board))

        if(turn == 1):
            turn = 2
        else:
            turn = 1

        gameState = getGameState(board) 

    return gameState

#update our weights based upon the training data from the last played game
#the weights are updated by comparing the estimated move value with the actual move value 
#values of 0, 100, & -100 are used for a draw, win, and loss
def updateWeights(weights, train, result, x):
    values = [0 for i in range(len(train))]
    if(result == 0):
        values[len(values)-1] = 0
    elif(result == x):
        values[len(values)-1] = 100
    else:
        values[len(values)-1] = -100

    for i in range(len(values)-1):
        values[i] = estimateMoveValue(getFeatures(train[i+1]), weights)

    for i in range(len(values)):
        board = train[i]
        features = getFeatures(board)
        value = values[i]
        estimate = estimateMoveValue(features, weights)

        #update our weights
        for j in range(len(weights)):
            weights[j] = weights[j] +(learnConstant*(value-estimate)*features[j])


#initialize our weights, the value of 0.5 is arbitrarily picked
initialWeight = 0.5
n_features = 6
oWeights = [initialWeight for i in range(n_features)]
xWeights = [initialWeight for i in range(n_features)]

trainingIterations = 10000
print("training our tic tac toe AI for %d games (this may take a minute or two...)" % trainingIterations)

for i in range(trainingIterations):
    xTrain, oTrain = [], []
    result = playGame(xWeights, oWeights, xTrain, oTrain)
    updateWeights(xWeights, xTrain, result, 1)
    updateWeights(oWeights, oTrain, result, 2)

print("finished training our tic tac toe AI!!!")
print("final weights: ")
print(xWeights)
print(oWeights)

print("launching the GUI, this allows the user to play against the AI")

#----------------------------------------------------
#------------------GUI Code--------------------------
#----------------------------------------------------

#determines if the game is still ongoing an updates the label correctly
def determineWinner():
    state = getGameState(theBoard)
    if(state == 0):
        winnerLabel['text'] = 'draw'
    elif(state == playerSide):
        winnerLabel['text'] = 'player wins'
    elif(state == computerSide):
        winnerLabel['text'] = 'computer wins'
    if(state != 3):
        for i in range(9):
            buttons[i]['state'] = 'disabled'
    return state

#update our tic tac toe board's graphical display
def updateButtons():
    for i in range(9):
        if(theBoard[i] != 0):
            b = buttons[i]
            if(theBoard[i] == 1):
                b['text'] = 'X'
            else:
                b['text'] = 'O'
            b['state'] = 'disabled'

#makes a computer move
def makeMove():
    if(computerSide == 1):
        makeBestMove(theBoard, xWeights, 1)
    else:
        makeBestMove(theBoard, oWeights, 2)
    updateButtons()
    winnerLabel['text'] = 'player turn'
    determineWinner()

#this function is called when on the board buttons are clicked
def buttonClick(n):
    theBoard[n] = playerSide
    updateButtons()
    winnerLabel['text'] = 'computer turn'
    state = determineWinner()
    if(state == 3):
        makeMove()

#this function starts a new tic tac toe game vs the AI
def newGameClick():
    global playerSide, computerSide, theBoard
    playerSide = playAsWhich.get()
    if(playerSide == 1):
        computerSide = 2
    else:
        computerSide = 1
    winnerLabel['text'] = 'game started'
    theBoard = [0 for x in range(9)]
    for b in buttons:
        b['text'] = '-'
        b['state'] = 'normal'

    if(computerSide == 1):
        makeMove()

#the following code sets up the Tkinter GUI for playing against the AI

root = Tk()
Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
root.minsize(width=600, height=600)
root.maxsize(width=600, height=600)
root.wm_title("Tic-Tac-Toe!!!")

frame = Frame(root)
frame.grid(row=0, column=0, sticky=N+S+E+W)

buttonFont = tkFont.Font(family='Helvetica', size=72, weight='bold')
buttons = []
i = 0
for r in range(3):
    for c in range(3):
        button = Button(frame, text="-", command=partial(buttonClick, i))
        button.grid(row=r, column=c, sticky=N+S+E+W)
        button['font'] = buttonFont
        button['state'] = 'disabled'
        buttons.append(button)
        i += 1

newGameButton = Button(frame, command=newGameClick, text="New Game?")
newGameButton.grid(row=3, column=0, sticky=N+S+E+W)

playAsWhich = IntVar() 
radioFrame = Frame(frame)
radioFrame.grid(row=3, column=1, sticky=N+S+E+W)
Grid.rowconfigure(radioFrame, 0, weight=1)
Grid.columnconfigure(radioFrame, 0, weight=1)
Grid.columnconfigure(radioFrame, 1, weight=1)

r1 = Radiobutton(radioFrame, text="X?", variable=playAsWhich, value=1)
r1.grid(row=0, column=0, sticky=N+S+E+W)
r1.invoke()
r2 = Radiobutton(radioFrame, text="O?", variable=playAsWhich, value=2)
r2.grid(row=0, column=1, sticky=N+S+E+W)

winnerLabel = Label(frame, text="new game")
winnerLabel.grid(row=3, column=2, sticky=N+S+W+E)

for r in range(4):
    Grid.rowconfigure(frame, r, weight=1)
for c in range(3):
    Grid.columnconfigure(frame, c, weight=1)

root.mainloop()
