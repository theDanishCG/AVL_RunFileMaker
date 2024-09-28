"""

This script is designed to read an input file, and generate a .run file for use
with Athena Vortex Lattice (AVL).

Visit https://web.mit.edu/drela/Public/web/avl/ for more information on AVL.

Author: Dane Jackson

Created: 09/26/2024

"""

import os
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
inFile = "input.csv"
templateFile = "template.run"
outFile = "cases.run"

varNames = []
alt = []
M = []
alpha = []
Beta = []
tempLines = []

inpComplete = "Input cases read successfully"

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