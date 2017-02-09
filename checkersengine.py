import re, tkFont
from Tkinter import *
from functools import partial
import copy

#the squares that a checker can move into from each position
blackMoveMapping = {1:[5, 6],
                    2:[6, 7],
                    3:[7, 8],
                    4:[8],
                    5:[9],
                    6:[9, 10],
                    7:[10, 11],
                    8:[11, 12],
                    9:[13, 14],
                    10:[14, 15],
                    11:[15, 16],
                    12:[16],
                    13:[17],
                    14:[17, 18],
                    15:[18, 19],
                    16:[19, 20],
                    17:[21, 22],
                    18:[22, 23],
                    19:[23, 24],
                    20:[24],
                    21:[25],
                    22:[25, 26],
                    23:[26, 27],
                    24:[27, 28],
                    25:[29, 30],
                    26:[30, 31],
                    27:[31, 32],
                    28:[32],
                    29:[],
                    30:[],
                    31:[],
                    32:[]}

whiteMoveMapping = {1:[],
                    2:[],
                    3:[],
                    4:[],
                    5:[1],
                    6:[1, 2],
                    7:[2, 3],
                    8:[3, 4],
                    9:[5, 6],
                    10:[6, 7],
                    11:[7, 8],
                    12:[8],
                    13:[9],
                    14:[9, 10],
                    15:[10, 11],
                    16:[11, 12],
                    17:[13, 14],
                    18:[14, 15],
                    19:[15, 16],
                    20:[16],
                    21:[17],
                    22:[17, 18],
                    23:[18, 19],
                    24:[19, 20],
                    25:[21, 22],
                    26:[22, 23],
                    27:[23, 24],
                    28:[24],
                    29:[25],
                    30:[25, 26],
                    31:[26, 27],
                    32:[27, 28]}

# in each list(for each position) first is the piece to be jumped over, second is
# the landing spot 
blackJumpMapping = {1:[[6, 10]],
                    2:[[6, 9], [7, 11]],
                    3:[[7, 10], [8, 12]],
                    4:[[8, 11]],
                    5:[[9, 14]],
                    6:[[9, 13], [10, 15]],
                    7:[[10, 14], [11, 16]],
                    8:[[11, 15]],
                    9:[[14, 18]],
                    10:[[14, 17], [15, 19]],
                    11:[[15, 18], [16, 20]],
                    12:[[16, 19]],
                    13:[[17, 22]],
                    14:[[17, 21], [18, 23]],
                    15:[[18, 22], [19, 24]],
                    16:[[19, 23]],
                    17:[[22, 26]],
                    18:[[22, 25], [23, 27]],
                    19:[[23, 26], [24, 28]],
                    20:[[24, 27]],
                    21:[[25, 30]],
                    22:[[25, 29], [26, 31]],
                    23:[[26, 30], [27, 32]],
                    24:[[27, 31]],
                    25:[],
                    26:[],
                    27:[],
                    28:[],
                    29:[],
                    30:[],
                    31:[],
                    32:[]}

whiteJumpMapping = {1:[],
                    2:[],
                    3:[],
                    4:[],
                    5:[],
                    6:[],
                    7:[],
                    8:[],
                    9:[[6, 2]],
                    10:[[6, 1], [7, 3]],
                    11:[[7, 2], [8, 4]],
                    12:[[8, 3]],
                    13:[[9, 6]],
                    14:[[9, 5], [10, 7]],
                    15:[[10, 6], [11, 8]],
                    16:[[11, 7]],
                    17:[[14, 10]],
                    18:[[14, 9], [15, 11]],
                    19:[[15, 10], [16, 12]],
                    20:[[16, 11]],
                    21:[[17, 14]],
                    22:[[17, 13], [18, 15]],
                    23:[[18, 14], [19, 16]],
                    24:[[19, 15]],
                    25:[[22, 18]],
                    26:[[22, 17], [23, 19]],
                    27:[[23, 18], [24, 20]],
                    28:[[24, 19]],
                    29:[[25, 22]],
                    30:[[25, 21], [26, 23]],
                    31:[[26, 22], [27, 24]],
                    32:[[27, 23]]}

kingMoveMapping =  {1:[[5], [6, 10, 15, 19, 24, 28]],
                    2:[[6, 9, 13], [7, 11, 16, 20]],
                    3:[[7, 10, 14, 17, 21], [8, 12]],
                    4:[[8, 11, 15, 18, 22, 25, 29]],
                    5:[[1], [9, 14, 18, 23, 27, 32]],
                    6:[[1], [2], [9, 13], [10, 15, 19, 24, 28]],
                    7:[[2], [3], [10, 14, 17, 21], [11, 16, 20]],
                    8:[[3], [4], [11, 15, 18, 22, 25, 29], [12]],
                    9:[[5], [6, 2], [13], [14, 18, 23, 27, 32]],
                    10:[[6, 1], [7, 3], [14, 17, 21], [15, 19, 24, 28]],
                    11:[[7, 2], [8, 4], [15, 18, 22, 25, 29], [16, 20]],
                    12:[[8, 3], [16, 19, 23, 26, 30]],
                    13:[[9, 6, 2], [17, 22, 26, 31]],
                    14:[[9, 5], [10, 7, 3], [17, 21], [18, 23, 27, 32]],
                    15:[[10, 6, 1], [11, 8, 4], [18, 22, 25, 29], [19, 24, 28]],
                    16:[[11, 7, 2], [12], [19, 23, 26, 30], [20]],
                    17:[[13], [14, 10, 7, 3], [21], [22, 26, 31]],
                    18:[[14, 9, 5], [15, 11, 8, 4], [22, 25, 29], [23, 27, 32]],
                    19:[[15, 10, 6, 1], [16, 12], [23, 26, 30], [24, 28]],
                    20:[[16, 11, 7, 2], [24, 27, 31]],
                    21:[[17, 14, 10, 7, 3], [25, 30]],
                    22:[[17, 13], [18, 15, 11, 8, 4], [25, 29], [26, 31]],
                    23:[[18, 14, 9, 5], [19, 16, 12], [26, 30], [27, 32]],
                    24:[[19, 15, 10, 6, 1], [20], [27, 31], [28]],
                    25:[[21], [22, 18, 15, 11, 8, 4], [29], [30]],
                    26:[[22, 17, 13], [23, 19, 16, 12], [30], [31]],
                    27:[[23, 18, 14, 9, 5], [24, 20], [31], [32]],
                    28:[[24, 19, 15, 10, 6, 1], [32]],
                    29:[[25, 22, 18, 15, 11, 8, 4]],
                    30:[[25, 21], [26, 23, 19, 16, 12]],
                    31:[[26, 22, 17, 13], [27, 24, 20]],
                    32:[[27, 23, 18, 14, 9, 5], [28]]}

moveMappings = {'w':whiteMoveMapping, 'b':blackMoveMapping}
jumpMappings = {'w':whiteJumpMapping, 'b':blackJumpMapping}

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
        board[i] = 3
    for i in range(20, 32):
        board[i] = 1

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

def getJumps(board, index, jumpMapping, enemyChecker, prev, result):
    #i == the jumped over spot, j == the landing spot
    for (i, j) in jumpMapping[index+1]:
        if(board[i-1] == enemyChecker and board[j-1] == 0):
            at = copy.deepcopy(prev)
            at.append([i , j])
            result.append(at)
            getJumps(board, j, jumpMapping, enemyChecker, at, result)

    return result 

def getAllPossibleJumps(board, turn):
    moves = []
    jumpMapping = jumpMappings[turn]

    allyChecker = 1 if(turn == 'w') else 3
    enemyChecker = 3 if(turn == 'w') else 1

    for i in range(32):
        if(board[i] == allyChecker):
            at = getJumps(board, i, jumpMapping, enemyChecker, [], [])
            if(at != []):
                for move in at:
                    moves.append([i+1, move])

    return moves

def getAllPossibleMoves(board, turn):
    moves = getAllPossibleJumps(board, turn)
    if(moves != []):
        print(moves)
        return moves
    moveMapping = moveMappings[turn]

    allyChecker = 1 if(turn == 'w') else 3
    enemyChecker = 3 if(turn == 'w') else 1
    allyKing = 2 if(turn == 'w') else 4
    enemyKing = 4 if(turn == 'w') else 2

    for i in range(32):
        if(board[i] == allyChecker):
            for j in moveMapping[i+1]:
                if(board[j-1] == 0):
                    moves.append([i, j-1])
        elif(board[i] == allyKing):
            for a in kingMoveMapping[i+1]:
                for j in a:
                    if(board[j-1] == 0):
                        moves.append([i, j-1])

    return moves

filePath = 'dataset/OCA_2.0.pdn'
#games = parsePdnFile(filePath)
board = makeBoard()
#print(getFeatures(board))
#print(evaluateBoard(board, makeInitialWeights()))
#print("finished parsing")

# GUI Code

def buttonClick(zeroIndex):
    oneIndex = zeroIndex+1
    for button in buttons:
        button['bg'] = 'grey'

buttonUpdateText = {0: '', 1:'w', 2:'wK', 3:'b', 4:'bK'}
def updateButtons():
    for i in range(32):
        buttons[i]['text'] = buttonUpdateText[board[i]] 

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
        button = Button(frame, text="", command=partial(buttonClick, i)) 
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

updateButtons()
root.mainloop()
