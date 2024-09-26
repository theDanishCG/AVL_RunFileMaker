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

varNames = []
alt = []
M = []
alpha = []
Beta = []

with open(inFile, 'r') as iF:
    for i, line in enumerate(iF):
        if i == 0:
            templine = line.split()
            for j, k in enumerate(templine):
                varNames.append(templine[j])
        else:
            templine = line.split(',')
            alt.append(templine[0])
            M.append(templine[1])
            alpha.append(templine[2])
            Beta.append(templine[3].removesuffix('\n'))
