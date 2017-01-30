from sklearn import metrics, tree, neighbors
from os import system

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#Author: Donovan Miller
#Date: 01/29/17
#Description: This code uses machine learning to classify tic tac toe end game
#   scenarios.  
#Requires: sci-kit learn machine learning library: scikit-learn.org 
#Requires: Tic-Tac-Toe Endgame Data Set from UC Irvine: https://archive.ics.uci.edu/ml/datasets/Tic-Tac-Toe+Endgame 
#-------------------------------------------------------------------------------------
#Run via Python 2.7
#Make sure to set the filePath variable to the location of the Tic-Tac-Toe
#   Endgame Data Set
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

#this function determines whether there is 3 x's/o's in a row
def threeInARow(board, x):
    a = board
    #horizontal
    if(a[0] == a[1] and a[0] == a[2] and a[0] == x): return True 
    if(a[3] == a[4] and a[3] == a[5] and a[3] == x): return True 
    if(a[6] == a[7] and a[6] == a[8] and a[6] == x): return True 

    #vertical
    if(a[0] == a[3] and a[0] == a[6] and a[0] == x): return True 
    if(a[1] == a[4] and a[1] == a[7] and a[1] == x): return True 
    if(a[2] == a[5] and a[2] == a[8] and a[2] == x): return True 

    #diagonal
    if(a[0] == a[4] and a[0] == a[8] and a[0] == x): return True 
    if(a[2] == a[4] and a[2] == a[6] and a[2] == x): return True 

    return False 

#this function returns whether the game is a draw, x win, or o win
def getTarget(board):
    if(threeInARow(board, 1)):
        return 1 #x win
    elif(threeInARow(board, 2)):
        return 2 #o win
    else:
        return 0 #draw

#0 == empty space, 1 == x space, 2 == o space
#this dictionary is used to help convert the data from the Data Set into
#   numbers this is necessary for our sk-learn classifier
dataConv = {'b':0, 'x':1, 'o':2}

#change the following to the location of the UC Irvine Tic-Tac-Toe Endgame Data Set:
filePath = 'datasets/tic-tac-toe-data/tic-tac-toe.data'
#load in the data from the dataset file
data = [line.strip().split(',') for line in open(filePath, 'r')]

#reformat the data from the data set
for a in data:
    a.pop(9) #remove the last column as we don't need it
    for i in range(len(a)):
        a[i] = dataConv[a[i]] #convert the data to the correct format

#set up the target (ie whether each game is won/lost/drawn) for our classifier
target = [getTarget(x) for x in data]

#use a decision tree classifier to eventually use machine learning to predict 
#   which boards are wins/losses/draws 
classifier = tree.DecisionTreeClassifier()

#try the KNeighborsClassifier on the data if you want, it is much less accurate
#   for this particular use case
#classifier = neighbors.KNeighborsClassifier()

classifier.fit(data, target) #fit our classifier to the dataset

#expected and predicted should be the same as in this case we have 100% accuracy
expected = target
#use our fitted classifier to predict what each answer is 
predicted = classifier.predict(data)

# the classifier should be able to get 100% accuracy as there is a finite
#   set of tic tac toe endgames
print("Classification report for classifier %s:\n%s\n"
              % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

#tree.export_graphviz(classifier, out_file='tree.dot') #export the decision tree
