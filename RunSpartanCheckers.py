import os, sys

rootDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, rootDir + '/src')
execfile(rootDir + '/src/SpartanCheckers.py')
