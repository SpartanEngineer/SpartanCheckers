import re, tkFont
from Tkinter import *

initialWeight = 0.5

class CheckersGame:
    def __init__(self, data):
        self.eventName = ""
        self.date = ""
        self.blackPlayer = ""
        self.whitePlayer = ""
        self.site = ""
        self.result = 0
        self.moves = []
        self.parse(data)

    def parse(self, data):
        n = len(data)
        lineNum = 0
        while(lineNum < n and data[lineNum][0] == '['):
            line = data[lineNum]
            if('"' in line):
                content = line.split('"')[1] #get the content in between quotes
                if(line.startswith('[Event')):
                    self.eventName = content
                elif(line.startswith('[Date')):
                    self.date = content 
                elif(line.startswith('[Black')):
                    self.blackPlayer = content
                elif(line.startswith('[White')):
                    self.whitePlayer = content
                elif(line.startswith('[Site')):
                    self.site = content
                elif(line.startswith('[Result')):
                    resultConv = {'1/2-1/2':0, '1-0':1, '0-1':2}
                    self.result = resultConv[content]
            lineNum += 1

        while(lineNum < n):
            line = re.compile("[0-9]+\.").split(data[lineNum])
            split2 = "".join(line).split(' ')
            for s in split2:
                if(s != ''):
                    self.moves.append(s)
            lineNum += 1

        self.moves.pop() #get rid of the game result (which is the last item in the split)

    def __str__(self):
        d = {}
        d['Event'] = self.eventName
        d['Date'] = self.date
        d['Black'] = self.blackPlayer
        d['White'] = self.whitePlayer
        d['Site'] = self.site
        d['Result'] = self.result
        #d['Moves'] = self.moves
        return str(d) 

def parsePdnFile(filePath):
    data = [line.strip() for line in open(filePath, 'r')]
    games = []
    lastLine = 0
    atLine = 0
    while(lastLine < len(data)):
        while(data[atLine] != ''):
            atLine += 1

        game = CheckersGame(data[lastLine:atLine])
        games.append(game)
        atLine += 1
        lastLine = atLine

    return games

#0 == empty
#1 == black checker
#2 == black king
#3 == white checker
#4 == white king
def makeBoard():
    board = [0 for x in range(32)]
    for i in range(12):
        board[i] = 1
    for i in range(20, 32):
        board[i] = 3

    return board

def makeInitialWeights():
    weights = []
    for i in range(4):
        a = [initialWeight for j in range(32)]
        weights.append(a)
    return weights

def getFeatures(board):
    features = []
    for i in range(1, 5):
        a = [1 if(x == i) else 0 for x in board]
        features.append(a)
    return features

def evaluateBoard(board, weights):
    features = getFeatures(board)
    value = 0
    for i in range(4):
        for j in range(32):
            value += (weights[i][j] * features[i][j])
    return value

filePath = 'dataset/OCA_2.0.pdn'
#games = parsePdnFile(filePath)
board = makeBoard()
#print(getFeatures(board))
#print(evaluateBoard(board, makeInitialWeights()))
#print("finished parsing")

# GUI Code

root = Tk()
Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
root.minsize(width=600, height=600)
root.maxsize(width=600, height=600)
root.wm_title("Checkers!!!")

frame = Frame(root)
frame.grid(row=0, column=0, sticky=N+S+E+W)

buttonFont = tkFont.Font(family='Helvetica', size=36, weight='bold')
buttons = []
i, j, num = 0, 0, 0
for r in range(8):
    num += 1
    if(num >= 2):
        num = 0
    for c in range(8):
        button = Button(frame, text="") 
        button.grid(row=r, column=c, sticky=N+S+E+W)
        button['font'] = buttonFont
        button['state'] = 'disabled'
        if(j % 2 == num):
            i += 1
            button['text'] = str(i)
            button['bg'] = 'grey'
            button['state'] = 'normal'
            buttons.append(button)

        j += 1

for r in range(8):
    Grid.rowconfigure(frame, r, weight=1)
for c in range(8):
    Grid.columnconfigure(frame, c, weight=1)

root.mainloop()
