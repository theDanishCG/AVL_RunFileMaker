"""

This script is designed to read an input file, and generate a .run file for use
with Athena Vortex Lattice (AVL).

Visit https://web.mit.edu/drela/Public/web/avl/ for more information on AVL.

Author: Dane Jackson

Created: 09/26/2024

"""

import os
import numpy as np
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
inFile = "input.csv"
templateFile = Path(str(dir_path) + "/data/template.run")
atmosFile = templateFile = Path(str(dir_path) + "/data/stdatmos.csv")
outFile = "cases.run"

varNames = []
alt = []
M = []
alpha = []
Beta = []
tempLines = []
altList = []
tempList = []
pList = []
rhoList = []
aList = []
muList = []

inpComplete = "Input cases read successfully"

with open(atmosFile, 'r') as aF:
    for i, line in enumerate(aF):
        if i > 2:
            templine = line.split(',')
            altList.append(templine[0])
            tempList.append(templine[1])
            pList.append(templine[2])
            rhoList.append(templine[3])
            aList.append(templine[4])
            muList.append(templine[5])

altArray = np.array(altList)
tempArray = np.array(tempList)
pArray = np.array(pList)
rhoArray = np.array(rhoList)
aArray = np.array(aList)
muArray = np.array(muList)

del altList, tempList, pList, rhoList, aList, muList

with open(inFile, 'r') as iF:
    print("Opening input file and reading variables")
    for i, line in enumerate(iF):
        if i == 0:
            templine = line.split()
            for j, k in enumerate(templine):
                varNames.append(templine[j])
        else:
            print("Reading inputs for case " + str(i) + " of " + str(len(varNames)))
            templine = line.split(',')
            alt.append(templine[0])
            M.append(templine[1])
            alpha.append(templine[2])
            Beta.append(templine[3].removesuffix('\n'))

print(inpComplete)

print("Formatting output run file")

with open(templateFile, 'r') as tF:
    for line in tF:
        tempLines.append(line)
print('Template format loaded')
#with open(outFile, 'w') as oF:
    #for i in len(alt):
        #for i, line in enumerate(tempLines):
        # Modify each

#def getAtmos(alt):
