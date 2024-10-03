"""

This script is designed to read an input file, and generate a .run file for use
with Athena Vortex Lattice (AVL).

Visit https://web.mit.edu/drela/Public/web/avl/ for more information on AVL.

Author: Dane Jackson

Created: 09/26/2024

"""

# import packages

import os
import numpy as np
from pathlib import Path

# define paths and files

dir_path = os.path.dirname(os.path.realpath(__file__))
inFile = "input.csv"
templateFile = Path(str(dir_path) + "/data/template.run")
atmosFile = Path(str(dir_path) + "/data/stdatmos.csv")
outFile = "cases.run"

# initialize lists

varNames = []
alt = []
M = []
alpha = []
Beta = []
cSurfs = []
dSurfs = []
tempLines = []
altList = []
tempList = []
pList = []
rhoList = []
aList = []
muList = []
caseatmos = []

# Create output messages

inpBegin = "Opening input file and reading variables"
inpComplete = "Input cases read successfully"
tempRead = "Reading template run file"

def getAtmos(alt):

    """
    This function interpolates standard atmospheric conditions
    for the given altitude
    """

    retCond = []

    retCond.append(np.interp(alt,altArray,tempArray))
    retCond.append(np.interp(alt,altArray,pArray))
    retCond.append(np.interp(alt,altArray,rhoArray))
    retCond.append(np.interp(alt,altArray,aArray))
    retCond.append(np.interp(alt,altArray,muArray))

    return retCond # Returns list of floats containing standard atmospheric
                   # conditions at provided altitude

# Reads standard atmospheric data for interpolation

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

# Converts atmospheric data lists into arrays and deletes lists

altArray = np.asarray(altList, dtype = np.float32)
tempArray = np.asarray(tempList, dtype = np.float32)
pArray = np.asarray(pList, dtype = np.float32)
rhoArray = np.asarray(rhoList, dtype = np.float32)
aArray = np.asarray(aList, dtype = np.float32)
muArray = np.asarray(muList, dtype = np.float32)

del altList, tempList, pList, rhoList, aList, muList

# Reads input file and creates lists of variables for all cases

print(inpBegin)
with open(inFile, 'r') as iF:
    for i, line in enumerate(iF):
        if i == 0:
            templine = line.removesuffix('/n').split(',')
            for j, k in enumerate(templine):
            # Should iterate through control surfaces and store names in a list
                if j >= 4:
                    for l in templine[4:]:
                        cSurfs.append(l)
                else:
                    varNames.append(templine[j])
        else:
            print("Reading inputs for case " + str(i))
            templine = line.removesuffix('\n').split(',')
            alt.append(templine[0])
            M.append(templine[1])
            alpha.append(templine[2])
            Beta.append(templine[3])
            for j in templine[4:]:
	            dSurfs.append(j)

print(inpComplete)

# Reads template run file to rebuild with case data

print(tempRead)

with open(templateFile, 'r') as tF:
    for line in tF:
        tempLines.append(line)

print('Template format loaded')

k = 0

with open(outFile, 'w') as oF:
    for i, caseAlt in enumerate(alt):
        print("Writing outputs for case " + str(i+1))
        caseAtmos = getAtmos(alt[i])
        for j, line in enumerate(tempLines):
            #print(line)
            if j == 1:
                line = line.replace('1', str(i+1)).replace('0.0',
                    str(alpha[i])).replace('0.60', str(M[i])).replace('SL',
                    str(int(alt[i])/1000) + " kft")
                oF.write(line)
            elif j == 3:
                line = line.replace('0.0', str(alpha[i]))
                oF.write(line)
            elif j == 4:
                line = line.replace('0.00000', str(Beta[i]))
                oF.write(line)
            elif j >= 8 and j < (8 + len(dSurfs)):
                line = line.replace('0.00000', str(dSurfs[k]))
                oF.write(line)
                k+=1
            else:
                oF.write(line)


print('Done')