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

# Index of beginning of control surfaces

csi = 9

# define paths and files

dir_path = os.path.dirname(os.path.realpath(__file__))
input_file = Path(str(dir_path) + '/input.csv')
template_file = Path(str(dir_path) + "/data/template.run")
atmos_file = Path(str(dir_path) + "/data/stdatmos.csv")
out_file = Path(str(dir_path) +"/cases.run")

# initialize lists

#varNames = []
alt = []
M = []
alpha = []
beta = []
C_D_0 = []
X_cg = []
I_xx = []
I_yy = []
I_zz = []
control_surfaces = []
surface_deflections = []
template_lines = []
altitudes = []
temperatures = []
pressures = []
densities = []
speeds_of_sound = []
viscosities = []
case_atmos = []

# Create output messages

input_begin = "Opening input file and reading variables"
input_complete = "Input cases read successfully"
template_read = "Reading template run file"
out_write = "Run file " + str(outFile) + " has been written successfully."

def get_atmos(alt): # getAtmos

    """
    This function interpolates standard atmospheric conditions
    for the given altitude
    """

    condition = []

    condition.append(np.interp(alt,altArray,tempArray))
    condition.append(np.interp(alt,altArray,pArray))
    condition.append(np.interp(alt,altArray,rhoArray))
    condition.append(np.interp(alt,altArray,aArray))
    condition.append(np.interp(alt,altArray,muArray))
    
    condition = tuple(condition)

    return condition # Returns list of floats containing standard atmospheric
                   # conditions at provided altitude

def replace_value(line, val): #repVal
    if line.startswith(' density'):
        new_line = line.replace('0.00000000', str("%.8f" % float(val)))
    elif line.startswith(' I') or line.startswith(' vel'):
        new_line = line.replace('0.00000', str("%.2f" % float(val)))
    else:
        new_line = line.replace('0.00000', str("%.5f" % float(val)))
    return new_line

# Reads standard atmospheric data for interpolation

with open(atmos_file, 'r') as aF:
    for i, line in enumerate(aF):
        if i > 2:
            templine = line.split(',')
            altitudes.append(templine[0])
            temperatures.append(templine[1])
            pressures.append(templine[2])
            densities.append(templine[3])
            speeds_of_sound.append(templine[4])
            viscosities.append(templine[5])

# Converts atmospheric data lists into arrays and deletes lists

altArray = np.asarray(altitudes, dtype = np.float32)
tempArray = np.asarray(temperatures, dtype = np.float32)
pArray = np.asarray(pressures, dtype = np.float32)
rhoArray = np.asarray(densities, dtype = np.float32)
aArray = np.asarray(speeds_of_sound, dtype = np.float32)
muArray = np.asarray(viscosities, dtype = np.float32)

del altitudes, temperatures, pressures, densities, speeds_of_sound, viscosities

# Reads input file and creates lists of variables for all cases

print(input_begin)
with open(input_file, 'r') as iF:
    for i, line in enumerate(iF):
        if i == 0:
            templine = line.removesuffix('\n').split(',')
            for j, k in enumerate(templine):
            # Should iterate through control surfaces and store names in a list
                if j >= csi:
                    #for l in templine[csi:]:
                    print(k)
                    control_surfaces.append(k)
                else:
                    continue; #varNames.append(templine[j])
        else:
            print("Reading inputs for case " + str(i))
            templine = line.removesuffix('\n').split(',')
            alt.append(templine[0])
            M.append(templine[1])
            alpha.append(templine[2])
            beta.append(templine[3])
            C_D_0.append(templine[4])
            X_cg.append(templine[5])
            I_xx.append(templine[6])
            I_yy.append(templine[7])
            I_zz.append(templine[8])
            for j in templine[csi:]:
	            surface_deflections.append(j)

print(input_complete)

# Reads template run file to rebuild with case data

print(template_read)

with open(template_file, 'r') as tF:
    for line in tF:
        template_lines.append(line)
        
template_lines = tuple(template_lines)

print('Template format loaded')

rv = replace_value

with open(out_file, 'w') as oF:
    for i, caseAlt in enumerate(alt):
        print("Writing outputs for case " + str(i+1))
        case_atmos = get_atmos(alt[i])
        k = 0
        for j, line in enumerate(template_lines):
            #print(line)
            if j == 1:
                line = line.replace('1', str(i+1)).replace('0.0',
                    str(alpha[i])).replace('0.60', str(M[i])).replace('SL',
                    str(int(alt[i])/1000) + " kft")
                oF.write(line)
            elif j == 3:
                line = line.replace('0.0', str("%.5f" % float(alpha[i])))
                oF.write(line)
            elif j == 4:
                oF.write(rv(line, beta[i]))
            elif j >= 8 and j < (8 + len(control_surfaces)):
                oF.write(rv(line, surface_deflections[k]))
                k+=1
            elif line.startswith(" alpha"):
                oF.write(rv(line, alpha[i]))
            elif line.startswith(" beta"):
                oF.write(rv(line, beta[i]))
            elif line.startswith(" Mach"):
                oF.write(rv(line, M[i]))
            elif line.startswith(" velocity"):
                v = float(M[i])*case_atmos[3]
                oF.write(rv(line, v))
            elif line.startswith(' density'):
                oF.write(rv(line, case_atmos[2]))
            elif line.startswith(' CDo'):
                oF.write(rv(line, C_D_0[i]))
            elif line.startswith(' X_cg'):
                oF.write(rv(line, X_cg[i]))
            elif line.startswith(' Ixx'):
                oF.write(rv(line, I_xx[i]))
            elif line.startswith(' Iyy'):
                oF.write(rv(line, I_yy[i]))
            elif line.startswith(' Izz'):
                oF.write(rv(line, I_zz[i]))
            elif line.startswith(' visc CM_u'):
                line = line + '\n'
                oF.write(line)
            else:
                oF.write(line)

print(out_write)