import tkinter
from tkinter import * 
from tkinter.font import Font
from enum import Enum

#python 3

class Pieces(Enum):
    wKing = 0
    wQueen = 1
    wRook = 2
    wBishop = 3
    wKnight = 4
    wPawn = 5
    bKing = 6
    bQueen = 7
    bRook = 8
    bBishop = 9
    bKnight = 10
    bPawn = 11
    empty = 12

unicodeConv = {Pieces.wKing : '♔',
               Pieces.wQueen : '♕',
               Pieces.wRook : '♖',
               Pieces.wBishop : '♗',
               Pieces.wKnight : '♘',
               Pieces.wPawn : '♙',
               Pieces.bKing : '♚',
               Pieces.bQueen : '♛',
               Pieces.bRook : '♜',
               Pieces.bBishop : '♝',
               Pieces.bKnight : '♞',
               Pieces.bPawn : '♟',
               Pieces.empty : ' '}

def makeBoard():
    board = [[Pieces.empty for x in range(8)] for y in range(8)]

    #setting up initial black positions
    board[0][0] = Pieces.bRook
    board[0][1] = Pieces.bKnight
    board[0][2] = Pieces.bBishop
    board[0][3] = Pieces.bQueen
    board[0][4] = Pieces.bKing
    board[0][5] = Pieces.bBishop
    board[0][6] = Pieces.bKnight
    board[0][7] = Pieces.bRook
    for i in range(8):
        board[1][i] = Pieces.bPawn

    #setting up inital white positions
    board[7][0] = Pieces.wRook
    board[7][1] = Pieces.wKnight
    board[7][2] = Pieces.wBishop
    board[7][3] = Pieces.wQueen
    board[7][4] = Pieces.wKing
    board[7][5] = Pieces.wBishop
    board[7][6] = Pieces.wKnight
    board[7][7] = Pieces.wRook
    for i in range(8):
        board[6][i] = Pieces.wPawn

    return board

def updateButtons(board, buttons):
    for r in range(8):
        for c in range(8):
            buttons[r][c]["text"] = unicodeConv[board[r][c]]

def checkerTheButtons(buttons):
    for r in range(8):
        i = 1 if(r % 2 == 0) else 0
        for c in range(8):
            if(i % 2 == 0):
                buttons[r][c]['bg'] = 'light grey'
            else:
                buttons[r][c]['bg'] = 'white'
            i += 1

board = makeBoard()

root = Tk()

Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
root.wm_title("Chess!!!")

topLevelFrame = Frame(root)
topLevelFrame.grid(row=0, column=0, sticky=N+S+E+W)

boardFrame = Frame(topLevelFrame)
boardFrame.grid(row=0, column=0, sticky=N+S+E+W)

Grid.rowconfigure(topLevelFrame, 0, weight=1)
Grid.columnconfigure(topLevelFrame, 0, weight=5)
Grid.columnconfigure(topLevelFrame, 1, weight=1)

chessFont = Font(family='Tahoma', size=36, weight='bold')
labelFont = Font(family='Tahoma', size=24, weight='normal')

buttons = []
labelConv = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}

for r in range(8):
    row = []
    for c in range(8):
        button = Button(boardFrame, text='♔')
        button.grid(row=r, column=c+1, sticky=N+S+E+W)
        button.configure(font=chessFont)
        row.append(button)

    colLabel = Label(boardFrame, text=str(abs(r-8)), font=labelFont)
    colLabel.grid(row=r, column=0, sticky=N+S+E+W)
    rowLabel = Label(boardFrame, text=labelConv[r+1], font=labelFont)
    rowLabel.grid(row=8, column=r+1, sticky=N+S+E+W)

    buttons.append(row)

updateButtons(board, buttons)
checkerTheButtons(buttons)
root.mainloop()
