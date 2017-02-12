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

filePath = 'dataset/OCA_2.0.pdn'
games = parsePdnFile(filePath)
print("finished parsing pdn file")
