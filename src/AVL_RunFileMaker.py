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

# Define paths and files

dir_path = os.path.dirname(os.path.realpath(__file__))
input_file = Path(str(dir_path) + '/input.csv')
template_file = Path(str(dir_path) + '/data/template.run')
atmos_file = Path(str(dir_path) + '/data/stdatmos.csv')
out_file = Path(str(dir_path) +'/cases.run')

# Initialize lists

input_parameters = []
ip = input_parameters
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

input_begin = 'Opening input file and reading variables'
input_complete = 'Input cases read successfully'
template_read = 'Reading template run file'
out_write = 'Run file ' + str(out_file) + ' has been written successfully.'

def get_input():
    # Reads input file and creates lists of variables for all cases

    print(input_begin)
    first_line = []
    with open(input_file, 'r') as iF:
        for i, line in enumerate(iF):
            temp_line = line.removesuffix('\n').split(',')
            if i == 0:
                for j, parameter in enumerate(temp_line):
                    if j >= csi:
                        first_line.append(parameter)
                        control_surfaces.append(parameter)
                    else:
                        first_line.append(parameter)
                        continue
            elif i == 1:
                for j, parameter in enumerate(temp_line):
                    for k in first_line:
                        if parameter != k:
                            first_line[j] = parameter
                        else:
                            continue
            else:
                print('Reading inputs for case ' + str(i-1))
                for j, parameter in enumerate(first_line):
                    for k, val in enumerate(temp_line):
                        if k == j:
                            ip.append(parameter.split())
                            ip[k].append(eval(val))
                            continue
                    for h in temp_line[csi:]:
                        surface_deflections.append(h)

    print(input_complete)

def get_atmos(alt):

    """
    This function interpolates standard atmospheric conditions
    for the given altitude
    """

    condition = []

    condition.append(np.interp(alt,altitudes,temperatures))
    condition.append(np.interp(alt,altitudes,pressures))
    condition.append(np.interp(alt,altitudes,densities))
    condition.append(np.interp(alt,altitudes,speeds_of_sound))
    condition.append(np.interp(alt,altitudes,viscosities))
    
    condition = tuple(condition)

    return condition    # Returns list of floats containing standard atmospheric
                        # conditions at provided altitude

def replace_value(line, val):
    if line.startswith(' density'):
        new_line = line.replace('0.00000000', str('%.8f' % float(val)))
    elif line.startswith(' I') or line.startswith(' vel'):
        new_line = line.replace('0.00000', str('%.2f' % float(val)))
    else:
        new_line = line.replace('0.00000', str('%.5f' % float(val)))
    return new_line

def control_surface_output(i):
    if control_surfaces[i] == ip[i+csi][0]:
        constraint = control_surfaces[i]

    else:
        constraint = ip[i+csi][0]

    num_spaces = 13 - len(control_surfaces[i])
    num_spaces_constraint = 12 - len(constraint)

    line = (' ' + control_surfaces[i] + num_spaces * ' ' + '->  ' +
            constraint + num_spaces_constraint * ' ' + '=   0.00000\n')
    
    line = rv(line, surface_deflections[k])

    return line

# Read standard atmospheric data for interpolation

with open(atmos_file, 'r') as aF:
    for i, line in enumerate(aF):
        if i > 2:
            temp_line = line.split(',')
            altitudes.append(temp_line[0])
            temperatures.append(temp_line[1])
            pressures.append(temp_line[2])
            densities.append(temp_line[3])
            speeds_of_sound.append(temp_line[4])
            viscosities.append(temp_line[5])

# Convert atmospheric data lists into arrays and deletes lists

altitudes = np.asarray(altitudes, dtype = np.float32)
temperatures = np.asarray(temperatures, dtype = np.float32)
pressures = np.asarray(pressures, dtype = np.float32)
densities = np.asarray(densities, dtype = np.float32)
speeds_of_sound = np.asarray(speeds_of_sound, dtype = np.float32)
viscosities = np.asarray(viscosities, dtype = np.float32)

get_input()

# Read template run file to rebuild with case data

print(template_read)

with open(template_file, 'r') as tF:
    for line in tF:
        template_lines.append(line)
        
# Convert to tuple to prevent accidental changes

template_lines = tuple(template_lines)

print('Template format loaded')

rv = replace_value

# Write output file

with open(out_file, 'w') as oF:
    # Begin loop for all cases
    for i, caseAlt in enumerate(ip[0]):
        if i == 0:
            continue    # Skip first iteration of input names
        print('Writing outputs for case ' + str(i))
        # Get atmospheric data for current case
        case_atmos = get_atmos(ip[0][i])
        # Begin loop through template for each case
        for j, line in enumerate(template_lines):
            # Replace case number and name with generic flight condition info
            if j == 1:
                line = line.replace('1', str(i)).replace('0.0',
                    str(ip[2][i])).replace('0.60', str(ip[1][i])).replace('SL',
                    str(int(ip[0][i])/1000) + ' kft')
                oF.write(line)
            # Replace angle of attack with appropriate constraint and value
            elif j == 3:
                line = line.replace('->  alpha', '->  ' + ip[2][0] +
                        ((len('alpha') - len(ip[2][0])) * ' '))
                line = line.replace('0.0', str('%.5f' % float(ip[2][i])))
                oF.write(line)
            # Replace sideslip angle with appropriate constraint and value
            elif j == 4:
                oF.write(rv(line, ip[3][i]))
            elif j == 8:
                k = 0
                while k < len(control_surfaces):
                    oF.write(control_surface_output(k))
                    k+=1
                if k == len(control_surfaces):
                    oF.write('\n')
            elif line.startswith(' alpha'):
                oF.write(rv(line, ip[2][i]))
            elif line.startswith(' beta'):
                oF.write(rv(line, ip[3][i]))
            elif line.startswith(' Mach'):
                oF.write(rv(line, ip[1][i]))
            elif line.startswith(' velocity'):
                v = float(ip[1][i])*case_atmos[3]
                oF.write(rv(line, v))
            elif line.startswith(' density'):
                oF.write(rv(line, case_atmos[2]))
            elif line.startswith(' CDo'):
                oF.write(rv(line, ip[4][i]))
            elif line.startswith(' X_cg'):
                oF.write(rv(line, ip[5][i]))
            elif line.startswith(' Ixx'):
                oF.write(rv(line, ip[6][i]))
            elif line.startswith(' Iyy'):
                oF.write(rv(line, ip[7][i]))
            elif line.startswith(' Izz'):
                oF.write(rv(line, ip[8][i]))
            elif line.startswith(' visc CM_u'):
                line = line + '\n'
                oF.write(line)
            else:
                oF.write(line)

print(out_write)