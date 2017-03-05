import re, tkFont, copy, random, time, tkMessageBox, json, os.path, ttk, math
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from functools import partial
from PIL import ImageTk
import multiprocessing
from multiprocessing import Process
from Queue import Empty, Queue

from checkersMoveMappings import *

weightsFileName = 'weights.json'
learnConstant = 0.1 #learning constant
initialWeight = 0.5

winValue = 100
lossValue = -100
drawValue = 0

def isNan(x):
    return math.isnan(x)

def isInf(x):
    return math.isinf(x) and x > 0

def isNegInf(x):
    return math.isinf(x) and x < 0

def setInf(x):
    if(isInf(x)):
        return winValue
    elif(isNegInf(x)):
        return lossValue
    else:
        return x

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
    weights.append([initialWeight for j in range(6)])
    return weights

def makeChinookWeights():
    weights = [initialWeight for i in range(14)]
    return weights

def hasPieces(board, turn):
    return 1 if(getNPieces(board, turn) > 0) else 0

def hasMoves(board, turn):
    return 1 if(len(getAllPossibleBoards(board, turn)) > 0) else 0

def piecesCanJump(board, turn):
    moves = getAllPossibleJumps(board, turn)
    result = 0
    for m in moves:
        result = max(result, len(m[1]))
    return result

def getFeatures(board):
    features = []
    for i in range(1, 5):
        a = [1 if(x == i) else 0 for x in board]
        features.append(a)

    b = [hasPieces(board, 'w'),
            hasPieces(board, 'b'),
            hasMoves(board, 'w'),
            hasMoves(board, 'b'),
            piecesCanJump(board, 'w'),
            piecesCanJump(board, 'b')]

    features.append(b)
    return features

#get the number of trapped kings
def getNTrapped(board, side):
    x = 2 if(side == 'w') else 4
    if(x == 2):
        enemyCheckers = [3, 4]
    else:
        enemyCheckers = [1, 2]

    result = 0
    for z in range(32):
        trapped = True
        if(board[z] == x):
            oneIndex = z+1
            for (iK, jK) in kingJumpMapping[oneIndex]:
                i, j = iK-1, jK-1
                if(board[i] in enemyCheckers and board[j] == 0):
                    trapped = False
                    break

            if(trapped):
                for i in kingMoveMapping[oneIndex]:
                    if(board[i-1] == 0):
                        trapped = False
                        break

        if(trapped == False):
            result += 1

    return result 

def isRunaway(board, index, backRow, moveMapping):
    zeroIndex = index-1
    if(zeroIndex in backRow):
        return board[zeroIndex] == 0
    if(board[zeroIndex] == 0):
        result = True
        for m in moveMapping[index]:
            result = (result and isRunaway(board, m, backRow, moveMapping))
        return result

    return False

def getNRunawayCheckers(board, side):
    x = 1 if(side == 'w') else 3
    moveMapping = moveMappings[side]
    enemyCheckers = [3, 4] if(side == 'w') else [1, 2]
    backRow = [0, 1, 2, 3] if(side == 'w') else [31, 30, 29, 28]
    spotsOpen = [False for x in range(4)]

    for i in range(4):
        if(not board[backRow[i]] in enemyCheckers):
            spotsOpen[i] = True

    if(spotsOpen == [False, False, False, False]):
        return 0

    result = 0
    for z in range(32):
        isTrue = True
        for m in moveMapping[z+1]:
            isTrue = (isTrue and isRunaway(board, m, backRow, moveMapping))

        if(isTrue):
            result += 1

    return result

def getChinookFeatures(board):
    #features:
    #piece count, kings count, trapped kings, turn, runaway checkers(free path
    #to king)
    features = [board.count(1),
                board.count(3),
                board.count(2),
                board.count(4),
                getNTrapped(board, 'w'),
                getNTrapped(board, 'b'),
                getNRunawayCheckers(board, 'w'),
                getNRunawayCheckers(board, 'b'),
                hasPieces(board, 'w'),
                hasPieces(board, 'b'),
                hasMoves(board, 'w'),
                hasMoves(board, 'b'),
                piecesCanJump(board, 'w'),
                piecesCanJump(board, 'b')]

    return features

def evaluateChinookFeatures(features, weights):
    value = 0
    for i in range(len(weights)):
        value += setInf(weights[i] * features[i])

    return value

def evaluateFeatures(features, weights):
    value = 0
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            value += (weights[i][j] * features[i][j])

    return value

def evaluateBoardChinook(board, weights):
    return evaluateChinookFeatures(getChinookFeatures(board), weights)

def evaluateBoard(board, weights):
    return evaluateBoardChinook(board, weights)
    #return evaluateFeatures(getFeatures(board), weights)

def evaluateBoardMinimax(board, depth, maximizingPlayer, turn, blackWeights,
        whiteWeights):
    if(depth == 0):
        weights = blackWeights if(turn == 'b') else whiteWeights
        return evaluateBoard(board, weights)

    boards = getAllPossibleBoards(board, turn)

    if(isGameOver(boards)):
        return winValue if(maximizingPlayer) else lossValue

    nextTurn = 'w' if(turn == 'b') else 'b'

    if maximizingPlayer == True:
        value = -float("inf")
        for b in boards:
            v = evaluateBoardMinimax(b, depth-1, False, nextTurn, weights) 
            value = max(value, v)
        return value
    else:
        value = float("inf")
        for b in boards:
            v = evaluateBoardMinimax(b, depth-1, True, nextTurn, weights)
            value = min(value, v)
        return value

def evaluateBoardAlphaBeta(board, depth, maximizingPlayer, alpha, beta, turn,
        blackWeights, whiteWeights):
    if(depth == 0):
        weights = blackWeights if(turn == 'b') else whiteWeights
        return evaluateBoard(board, weights)

    boards = getAllPossibleBoards(board, turn)

    if(isGameOver(boards)):
        return winValue if(maximizingPlayer) else lossValue

    nextTurn = 'w' if(turn == 'b') else 'b'

    if(maximizingPlayer):
        value = -float("inf")
        for b in boards:
            value = max(value, evaluateBoardAlphaBeta(board, depth-1, False,
                alpha, beta, nextTurn, blackWeights, whiteWeights))
            alpha = max(alpha, value)
            if(beta <= alpha):
                break

        return value
    else:
        value = float("inf")
        for b in boards:
            value = min(value, evaluateBoardAlphaBeta(board, depth-1, True, alpha,
                beta, nextTurn, blackWeights, whiteWeights))
            beta = min(beta, value)
            if(beta <= alpha):
                break

        return value

def updateWeights(trainingData, weights, didWin):
    n = len(trainingData)
    estimates = [evaluateBoard(x, weights) for x in trainingData]
    values = [0 for x in range(n)]
    if(didWin == 0):
        values[len(values)-1] = winValue 
    elif(didWin == 1):
        values[len(values)-1] = lossValue 
    else:
        values[len(values)-1] = drawValue 

    for i in range(n-1):
        values[i] = estimates[i+1]

    for i in range(n):
        board = trainingData[i]
        features = getChinookFeatures(board)
        value = setInf(values[i])
        estimate = setInf(estimates[i])

        #print(value, estimate, weights, features)

        #update our weights
        for j in range(len(weights)):
            if(features[j] != 0):
                weights[j] = setInf(weights[j] +
                        (learnConstant*(value-estimate)*features[j]))
            #for k in range(len(weights[j])):
                #weights[j][k] = weights[j][k] + (learnConstant*(value-estimate)*features[j][k])

def chooseMaximumBoard(values, boards):
    maxValue = values[0]
    maxBoard = boards[0]

    for i in range(1, len(boards)):
        if(values[i] > maxValue):
            maxValue = values[i]
            maxBoard = boards[i]

    return maxBoard

def getBestPossibleBoard(boards, weights):
    values = [evaluateBoard(b, weights) for b in boards]
    return chooseMaximumBoard(values, boards)

def getBestPossibleBoardMinimax(boards, side, blackWeights, whiteWeights, depth=3):
    if(len(boards) == 1):
        return boards[0]

    turn = side
    values = [evaluateBoardMinimax(b, depth, True, turn, blackWeights,
        whiteWeights) for b in boards]

    return chooseMaximumBoard(values, boards)

def evaluateAlphaBetaMapper(a):
    return evaluateBoardAlphaBeta(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7])

def getBestPossibleBoardAlphaBeta(boards, side, blackWeights, whiteWeights, depth=3):
    if(len(boards) == 1):
        return boards[0]

    turn = side
    #use the multiprocessing.Pool() to multi-thread our board evaluations
    pool = multiprocessing.Pool()

    a = [(b, depth, True, -float("inf"), float("inf"), turn, blackWeights,
        whiteWeights) for b in boards]
    values = pool.map(evaluateAlphaBetaMapper, a)

    return chooseMaximumBoard(values, boards)

def getJumps(board, index, jumpMapping, enemyCheckers, prev, result):
    #i == the jumped over spot, j == the landing spot
    for (iK, jK) in jumpMapping[index+1]:
        i, j = iK-1, jK-1
        if(board[i] in enemyCheckers and board[j] == 0):
            at = copy.deepcopy(prev)
            at.append([i , j])
            result.append(at)
            getJumps(board, j, jumpMapping, enemyCheckers, at, result)

    return result 

def getKingJumps(board, index, allyKing, enemyCheckers, prev, result):
    for (iK, jK) in kingJumpMapping[index+1]:
        i, j = iK-1, jK-1
        if(board[i] in enemyCheckers and board[j] == 0):
            #set up the next board... we need to make sure the king can't jump
            #back over where it just jumped
            newBoard = copy.deepcopy(board)
            newBoard[index] = 0
            newBoard[i] = 0
            newBoard[j] = allyKing
            at = copy.deepcopy(prev)
            at.append([i, j])
            result.append(at)
            getKingJumps(newBoard, j, allyKing, enemyCheckers, at, result)

    return result 

def getAllPossibleJumps(board, turn):
    moves = []
    jumpMapping = jumpMappings[turn]

    allyChecker = 1 if(turn == 'w') else 3
    enemyChecker = 3 if(turn == 'w') else 1
    allyKing = 2 if(turn == 'w') else 4
    enemyKing = 4 if(turn == 'w') else 2
    enemyCheckers = [enemyChecker, enemyKing]

    for i in range(32):
        if(board[i] == allyChecker):
            at = getJumps(board, i, jumpMapping, enemyCheckers, [], [])
            if(at != []):
                for move in at:
                    moves.append([i, move])
        elif(board[i] == allyKing):
            at = getKingJumps(board, i, allyKing, enemyCheckers, [], [])
            if(at != []):
                for move in at:
                    moves.append([i, move])

    return moves

def getAllPossibleMoves(board, turn):
    moves = []
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
            for j in kingMoveMapping[i+1]:
                if(board[j-1] == 0):
                    moves.append([i, j-1])

    return moves

def crownPieces(board):
    for i in range(0, 4):
        if(board[i] == 1):
            board[i] = 2

    for i in range(28, 32):
        if(board[i] == 3):
            board[i] = 4

def getAllPossibleBoards(board, turn):
    boards = []
    jumps = getAllPossibleJumps(board, turn)
    if(jumps != []):
        for (i, moves) in jumps:
            newBoard = copy.deepcopy(board)
            for (j, k) in moves:
                newBoard[j] = 0
            newPosition = moves[len(moves)-1][1]
            newBoard[newPosition] = newBoard[i]
            newBoard[i] = 0
            crownPieces(newBoard)
            boards.append(newBoard)
    else:
        moves = getAllPossibleMoves(board, turn)
        for (i, j) in moves:
            newBoard = copy.deepcopy(board)
            newBoard[j] = newBoard[i]
            newBoard[i] = 0
            crownPieces(newBoard)
            boards.append(newBoard)

    return boards

def isGameOver(boards):
    return boards == []

def getRandomBoard(boards):
    randomNum = random.randint(0, len(boards)-1)
    return boards[randomNum]

def getNPieces(board, color):
    if(color == 'w'):
        return board.count(1) + board.count(2)
    else:
        return board.count(3) + board.count(4)

def piecesChanged(board, nWhitePieces, nBlackPieces):
    nWhitePieces2 = getNPieces(board, 'w')
    nBlackPieces2 = getNPieces(board, 'b')

    if(nWhitePieces != nWhitePieces2 or nBlackPieces != nBlackPieces2):
        nWhitePieces = nWhitePieces2
        nBlackPieces = nBlackPieces2
        return True 
    else:
        return False 

def updateAiProgress(whichAi, threadSafeQueue, i, iterations, startTime):
    x = i+1.0
    amt = int((x / iterations) * 100)
    timeRunning = time.time() - startTime
    timePer = timeRunning / x
    timeLeft = int(timePer * (iterations - x))
    if(whichAi == 'b'):
        threadSafeQueue.put(['blackEstimate', timeLeft])
        threadSafeQueue.put(['blackProgress', amt])
    else:
        threadSafeQueue.put(['whiteEstimate', timeLeft])
        threadSafeQueue.put(['whiteProgress', amt])

def trainBlackAi(queue, iterations, movesToDraw, threadSafeQueue):
    blackWeights = makeChinookWeights()
    iterationsDoubled = iterations*2
    startTime = time.time()

    #train the black AI against a random AI
    for i in range(iterations):
        turn = 'b'
        board = makeBoard()
        boards = getAllPossibleBoards(board, turn)
        trainingData = []
        nWhitePieces = 12
        nBlackPieces = 12
        turnsSinceCaptured = 0
        while(not isGameOver(boards) and turnsSinceCaptured < movesToDraw):
            if(turn == 'b'):
                bestBoard = getBestPossibleBoard(boards, blackWeights)
                board = bestBoard
                trainingData.append(board) 
                turn = 'w'
            else:
                randomBoard = getRandomBoard(boards)
                board = randomBoard
                turn = 'b'

            if(piecesChanged(board, nWhitePieces, nBlackPieces) == False):
                turnsSinceCaptured = 0
            else:
                turnsSinceCaptured += 1

            boards = getAllPossibleBoards(board, turn)

        didWin = 0 if(turn == 'b') else 1
        if(turnsSinceCaptured >= movesToDraw):
            didWin = 2
        updateWeights(trainingData, blackWeights, didWin)

        updateAiProgress('b', threadSafeQueue, i, iterations, startTime)

    queue.put(blackWeights)

def trainWhiteAi(queue, iterations, movesToDraw, threadSafeQueue):
    whiteWeights = makeChinookWeights()
    iterationsDoubled = iterations*2
    startTime = time.time()

    #train the white AI against a random AI
    for i in range(iterations):
        turn = 'b'
        board = makeBoard()
        boards = getAllPossibleBoards(board, turn)
        trainingData = []
        nWhitePieces = 12
        nBlackPieces = 12
        turnsSinceCaptured = 0
        while(not isGameOver(boards) and turnsSinceCaptured < movesToDraw):
            if(turn == 'b'):
                randomBoard = getRandomBoard(boards)
                board = randomBoard
                turn = 'w'
            else:
                bestBoard = getBestPossibleBoard(boards, whiteWeights)
                board = bestBoard
                trainingData.append(board) 
                turn = 'b'

            if(piecesChanged(board, nWhitePieces, nBlackPieces) == False):
                turnsSinceCaptured = 0
            else:
                turnsSinceCaptured += 1

            boards = getAllPossibleBoards(board, turn)

        didWin = 0 if(turn == 'w') else 1
        if(turnsSinceCaptured >= movesToDraw):
            didWin = 2
        updateWeights(trainingData, whiteWeights, didWin)

        updateAiProgress('w', threadSafeQueue, i, iterations, startTime)

    queue.put(whiteWeights)

def timeRunningUpdater(q, threadSafeQueue, startTime):
    while(q.qsize() <= 0):
        timeRunning = time.time() - startTime 
        s = 'Time running: {0} seconds'.format(int(timeRunning))
        threadSafeQueue.put(['running', s])
        if(timeRunning > 605000):
            break
        time.sleep(1)

class ThreadSafeAiGui(Text):
    def __init__(self, master, q, guiDict, processes, queues, startTime,
            iterations, timeRunningQueue, **options):
        Text.__init__(self, master, **options)
        self.guiDict = guiDict 
        self.q = q
        self.processes = processes
        self.queues = queues
        self.startTime = startTime
        self.iterations = iterations
        self.timeRunningQueue = timeRunningQueue
        self.whiteEstimate = 0
        self.blackEstimate = 0
        self.updateGui()

    def updateGui(self):
        try:
            while self.q.qsize() > 0:
                data = self.q.get(block=False)
                obj = self.guiDict[data[0]]
                if(obj[0] == 'label'):
                    if(data[0] == 'blackEstimate' or data[0] ==
                            'whiteEstimate'):
                        if(data[0] == 'whiteEstimate'):
                            self.whiteEstimate = data[1]
                        else:
                            self.blackEstimate = data[1]
                        self.estimate = max(self.whiteEstimate, self.blackEstimate)
                        obj[1]['text'] = 'Est. {0} seconds left.'.format(self.estimate)
                    else:
                        obj[1]['text'] = data[1]
                else:
                    obj[1].set(data[1])
                self.update_idletasks() 
        except Empty:
            pass

        done = True
        for p in self.processes:
            if(p.is_alive()):
                done = False
                break

        if(done == False):
            self.master.after(100, self.updateGui)
        else:
            setWeights(self.startTime, self.queues[0], self.queues[1],
                    self.iterations, self.timeRunningQueue)

def setWeights(startTime, blackQueue, whiteQueue, iterations, timeRunningQueue):
    global blackWeights, whiteWeights, theWeights
    blackWeights = blackQueue.get()
    whiteWeights = whiteQueue.get()
    theWeights = [blackWeights, whiteWeights]
    print(theWeights)
    endTime = time.time()
    print("Training {0} iterations took: {1}".format(iterations, str(endTime-startTime)))
    timeRunningQueue.put(0)

def trainAi(iterations, topLevel, progressVars, timeLabels):
    #training our AI
    print("We will now train our AI using {0} iterations... this may take a while".format(iterations))
    startTime = time.time()
    movesToDraw = 50

    if(progressVars != None and topLevel != None):
        progressVars[0].set(0)
        progressVars[1].set(0)
        topLevel.update()

    threadSafeQueue = multiprocessing.Queue()

    blackQueue = multiprocessing.Queue()
    whiteQueue = multiprocessing.Queue()
    process1 = Process(target=trainBlackAi, args=(blackQueue, iterations,
        movesToDraw, threadSafeQueue))
    process2 = Process(target=trainWhiteAi, args=(whiteQueue, iterations,
        movesToDraw, threadSafeQueue))

    timeRunningQueue = multiprocessing.Queue()
    timeRunningProcess = Process(target=timeRunningUpdater,
            args=(timeRunningQueue, threadSafeQueue, startTime))

    timeRunningProcess.start()
    process1.start()
    process2.start()

    guiDict = {'running':['label', timeLabels[1]],
            'blackProgress':['progress', progressVars[0]],
            'whiteProgress':['progress', progressVars[1]],
            'blackEstimate':['label', timeLabels[0]],
            'whiteEstimate':['label', timeLabels[0]]}

    threadSafeGui = ThreadSafeAiGui(topLevel, threadSafeQueue,
            guiDict, [process1, process2], [blackQueue,
                whiteQueue], startTime, iterations, timeRunningQueue)

#might be a good idea to validate that the json conforms to some schema in the future
def loadWeightsFromJson(fileName):
    if(os.path.isfile(fileName)):
        with open(fileName, 'r') as infile:
            global blackWeights, whiteWeights
            theWeights = json.load(infile)
            blackWeights = theWeights[0]
            whiteWeights = theWeights[1]

def saveWeightsToJson(fileName, blackWeights, whiteWeights):
    with open(fileName, 'w') as outfile:
        json.dump([blackWeights, whiteWeights], outfile)

def openJsonFile():
    fileName = askopenfilename(filetypes=[('json files', '.json')])
    if(isinstance(fileName, (str, unicode))):
        loadWeightsFromJson(fileName)
        print('loaded weights from: {0}'.format(fileName))

def saveJsonFile():
    fileName = asksaveasfilename(filetypes=[('json files', '.json')])
    if(isinstance(fileName, (str, unicode))):
        saveWeightsToJson(fileName, blackWeights, whiteWeights)
        print('saved weights to: {0}'.format(fileName))

def cancelAiTraining(topLevel):
    topLevel.grab_release()
    topLevel.destroy()

def startAiTraining(iterationEntry, topLevel, progressVars, timeLabels):
    try:
        iterations = int(iterationEntry.get())
    except ValueError:
        print('iterations must be a valid integer value')
    else:
        trainAi(iterations, topLevel, progressVars, timeLabels)

def doAiTraining(root):
    #defining our pop up form
    topLevel = Toplevel()
    topLevel.minsize(width=600, height=200)
    topLevel.grab_set()
    topLevel.wm_title("Train a new AI!")

    iterationLabel = Label(topLevel, text='# of training iterations:')
    iterationLabel.grid(row=0, column=0, sticky=N+S+E+W)
    iterationEntry = Entry(topLevel)
    iterationEntry.insert(0, '100')
    iterationEntry.grid(row=0, column=1, sticky=N+S+E+W)

    blackLabel = Label(topLevel, text='BlackAI:')
    blackLabel.grid(row=1, column=0, sticky=N+S+E+W)
    blackAIProgress = IntVar()
    blackBar = ttk.Progressbar(topLevel, variable=blackAIProgress, maximum=100)
    blackBar.grid(row=1, column=1, sticky=N+S+E+W)

    whiteLabel = Label(topLevel, text='WhiteAI:')
    whiteLabel.grid(row=2, column=0, sticky=N+S+E+W)
    whiteAIProgress = IntVar()
    whiteBar = ttk.Progressbar(topLevel, variable=whiteAIProgress, maximum=100)
    whiteBar.grid(row=2, column=1, sticky=N+S+E+W)

    estimateLabel = Label(topLevel, text='Est: 0 seconds left')
    estimateLabel.grid(row=3, column=0, sticky=N+S+E+W)
    timeLabel = Label(topLevel, text='Time running: 0 seconds')
    timeLabel.grid(row=3, column=1, sticky=N+S+E+W)

    buttonStart = Button(topLevel, text='Start',
            command=partial(startAiTraining, iterationEntry
                , topLevel, [blackAIProgress, whiteAIProgress] , [estimateLabel, timeLabel]))
    buttonStart.grid(row=4, column=0, sticky=N+S+E+W)
    buttonCancel = Button(topLevel, text='Done', command=partial(cancelAiTraining, topLevel))
    buttonCancel.grid(row=4, column=1, sticky=N+S+E+W)

    for i in range(5):
        Grid.rowconfigure(topLevel, i, weight=1)
    for i in range(2):
        Grid.columnconfigure(topLevel, i, weight=1)

#we add this if statement so windows multithreading works correctly
if __name__ == '__main__':
    blackWeights = makeInitialWeights()
    whiteWeights = makeInitialWeights()

    loadWeightsFromJson(weightsFileName)

    print("--------------------")
    print('blackWeights:')
    print("--------------------")
    print(blackWeights)
    print("--------------------")
    print('whiteWeights:')
    print("--------------------")
    print(whiteWeights)
    print("--------------------")

    board = makeBoard()

# GUI Code
    currentGameOngoing = False
    weightsMapping = {'b': blackWeights, 'w': whiteWeights}

def newGameClick():
    startGame(playAsWhich.get() == 0)

def displayMovesClick():
    global currentGameOngoing
    if(currentGameOngoing):
            displayAllPossibleJumpsOrMoves(currentJumps, currentMoves)

def startGame(playerFirst):
    global pieceSelected, currentIndexes, currentJumps, currentMoves
    global currentTurn, currentBoards, currentGameOngoing
    global playerTurn, computerTurn, board

    board = makeBoard()
    pieceSelected = False
    currentTurn = 'b'
    currentJumps = getAllPossibleJumps(board, 'b')
    currentMoves = getAllPossibleMoves(board, 'b')
    currentBoards = getAllPossibleBoards(board, 'b')
    currentIndexes = {} 
    currentGameOngoing = True
    currentGameWinner = 'b'
    playerTurn = 'b' if(playerFirst) else 'w'
    computerTurn = 'w' if(playerFirst) else 'b'

    updateButtons(board)
    if(computerTurn == 'b'):
        doComputerTurn()
    statusLabel['text'] = 'Player turn'

def displayAllPossibleJumpsOrMoves(jumps, moves):
    if(jumps != []):
        for(i, moves) in jumps:
            buttons[i]['bg'] = 'green'
            for (j, k) in moves:
                buttons[j]['bg'] = 'red'
                buttons[k]['bg'] = 'blue'
    else:
        for (i, j) in moves:
            buttons[i]['bg'] = 'green'
            buttons[j]['bg'] = 'blue'

def displayPossibleJumpsOrMoves(board, jumps, moves, index):
    global currentIndexes
    currentIndexes = {}
    result = False
    if(jumps != []):
        for(i, moves) in jumps:
            if(i == index):
                result = True
                buttons[i]['bg'] = 'green'
                for (j, k) in moves:
                    buttons[j]['bg'] = 'red'
                    buttons[k]['bg'] = 'blue'
                    currentIndexes[k] = [i, moves] 
    else:
        for (i, j) in moves:
            if(i == index):
                result = True
                buttons[i]['bg'] = 'green'
                buttons[j]['bg'] = 'blue'
                currentIndexes[j] = [i]

    return result

def nextTurn():
    global board, currentJumps, currentMoves, currentIndexes, currentBoards
    global currentGameOngoing, currentTurn
    crownPieces(board)
    updateButtons(board)
    if(currentTurn == 'b'):
        currentTurn = 'w'
    else:
        currentTurn = 'b'
    currentJumps = getAllPossibleJumps(board, currentTurn)
    currentMoves = getAllPossibleMoves(board, currentTurn)
    currentIndexes = {}
    currentBoards = getAllPossibleBoards(board, currentTurn)
    if(isGameOver(currentBoards)):
        winner = 'black' if(currentTurn == 'w') else 'white'
        statusLabel['text'] = '{0} wins!'.format(winner)
        tkMessageBox.showinfo('Game Over!', 'Game is over: {0} wins!'.format(winner))
        currentGameOngoing = False

def doComputerTurn():
    statusLabel['text'] = 'computer turn'
    weights = weightsMapping[computerTurn] 
    global board
    #board = getBestPossibleBoard(currentBoards, weights)
    #board = getBestPossibleBoardMinimax(currentBoards, computerTurn,
    #        blackWeights, whiteWeights, 4)
    board = getBestPossibleBoardAlphaBeta(currentBoards, computerTurn,
            blackWeights, whiteWeights, 6)
    nextTurn()
    statusLabel['text'] = 'player turn'

def buttonClick(zeroIndex):
    global currentGameOngoing, currentTurn, playerTurn
    if(not currentGameOngoing or not currentTurn == playerTurn):
        return
    global pieceSelected, currentIndexes, currentJumps, currentMoves
    global currentBoards
    updateButtons(board)
    if(pieceSelected == True and zeroIndex in currentIndexes):
        pieceSelected = False
        startIndex = currentIndexes[zeroIndex][0]
        board[zeroIndex] = board[startIndex]
        board[startIndex] = 0

        #handle jumps
        if(len(currentIndexes[zeroIndex]) > 1):
            for (i, j) in currentIndexes[zeroIndex][1]:
                board[i] = 0
                if(j == zeroIndex):
                    break
        
        nextTurn()
        if(currentGameOngoing):
            doComputerTurn()
    else:
        pieceSelected = displayPossibleJumpsOrMoves(board, currentJumps, currentMoves, zeroIndex)

def updateButtons(board):
    for i in range(32):
        buttons[i]['bg'] = 'grey'
        buttons[i].config(image=buttonUpdateImage[board[i]])

#we add this if statement so windows multithreading works correctly
if __name__ == '__main__':
    root = Tk()

    #you have to make the images after instatiating the root Tkinter window for some
    #weird reason
    imagesFolder = 'resources'
    separator = '/'
    emptyCheckerImage = ImageTk.PhotoImage(file=imagesFolder + separator + 'emptyChecker.png') 
    whiteCheckerImage = ImageTk.PhotoImage(file=imagesFolder + separator + 'whiteChecker.png')
    blackCheckerImage = ImageTk.PhotoImage(file=imagesFolder + separator + 'blackChecker.png')
    whiteCheckerKingImage = ImageTk.PhotoImage(file=imagesFolder + separator + 'whiteCheckerKing.png')
    blackCheckerKingImage = ImageTk.PhotoImage(file=imagesFolder + separator + 'blackCheckerKing.png')
    buttonUpdateImage = {0: emptyCheckerImage, 1:whiteCheckerImage, 2:whiteCheckerKingImage,
            3:blackCheckerImage, 4:blackCheckerKingImage}

    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    root.wm_title("Checkers!!!")

    topLevelFrame = Frame(root)
    topLevelFrame.grid(row=0, column=0, sticky=N+S+E+W)

    boardFrame = Frame(topLevelFrame)
    boardFrame.grid(row=0, column=0, sticky=N+S+E+W)

    Grid.rowconfigure(topLevelFrame, 0, weight=1)
    Grid.columnconfigure(topLevelFrame, 0, weight=5)
    Grid.columnconfigure(topLevelFrame, 1, weight=1)

    buttonFont = tkFont.Font(family='Helvetica', size=24, weight='bold')
    buttons = []
    i, j, num = 0, 0, 0
    for r in range(8):
        num += 1
        if(num >= 2):
            num = 0
        for c in range(8):
            button = Button(boardFrame, text="", command=partial(buttonClick, i)) 
            button.grid(row=r, column=c, sticky=N+S+E+W)
            button['font'] = buttonFont
            button['bg'] = 'white'
            button['state'] = 'disabled'
            if(j % 2 == num):
                i += 1
                button['text'] = str(i) #this displays the index for each board position
                button['bg'] = 'grey'
                button['state'] = 'normal'
                buttons.append(button)

            j += 1

    for r in range(8):
        Grid.rowconfigure(boardFrame, r, weight=1)
    for c in range(8):
        Grid.columnconfigure(boardFrame, c, weight=1)

    optionsFrame = Frame(topLevelFrame)
    optionsFrame.grid(row=0, column=1, sticky=N+S+E+W)

    newGameButton = Button(optionsFrame, text="New Game?", command=newGameClick)
    newGameButton.grid(row=0, column=0, sticky=N+S+E+W)

    playAsWhich = IntVar() 
    radio1 = Radiobutton(optionsFrame, text="Play as black?", variable=playAsWhich, value=0)
    radio1.grid(row=1, column=0, sticky=N+S+E+W)
    radio1.invoke()
    radio2 = Radiobutton(optionsFrame, text="Play as white?", variable=playAsWhich, value=1)
    radio2.grid(row=2, column=0, sticky=N+S+E+W)

    displayMovesButton = Button(optionsFrame, text="Display moves", command=displayMovesClick)
    displayMovesButton.grid(row=3, column=0, sticky=N+S+W+E)

    statusLabel = Label(optionsFrame, text="click new game!")
    statusLabel.grid(row=4, column=0, sticky=N+S+W+E)

    loadAIButton = Button(optionsFrame, text="Load AI", command=openJsonFile)
    loadAIButton.grid(row=5, column=0, sticky=N+S+W+E)

    saveAIButton = Button(optionsFrame, text="Save AI", command=saveJsonFile)
    saveAIButton.grid(row=6, column=0, sticky=N+S+W+E)

    trainAIButton = Button(optionsFrame, text="Train AI", command=partial(doAiTraining, root))
    trainAIButton.grid(row=7, column=0, sticky=N+S+W+E)

    for i in range(8):
        Grid.rowconfigure(optionsFrame, i, weight=1)
    Grid.rowconfigure(optionsFrame, 8, weight=20)
    Grid.columnconfigure(optionsFrame, 0, weight=1)

    updateButtons(board)
    root.mainloop()
