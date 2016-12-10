# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:44:35 2016

@author: AZhang1
"""
import pandas as pd
import re

Location1 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\MTAB_ParkingResolutions_2002_to_2015_JP_V3.xlsx'
unknownonlyregulations0 = pd.read_excel(Location1, header = 0)

unknownonlyregulations = unknownonlyregulations0.where((pd.notnull(unknownonlyregulations0)),None)

'''
Fills in all empty cells with the last populated cell in the column
'''
def backtrack(indexnum, data_frame, column_num):
    textchunk = data_frame.iloc[indexnum,column_num]
    if textchunk == None or str(textchunk) == 'NaT':
        indexnum = indexnum - 1
        return backtrack(indexnum, data_frame, column_num)
    else:
        return textchunk

def backtrackreplace(dataframe, column_num):
    index = 0
    for item in range(len(dataframe.iloc[:, column_num])):
        dataframe.iloc[index,column_num] = backtrack(index, dataframe, column_num)
        index += 1
    return dataframe

'''
Fills in the regulation by identifying the all-caps words to the left in the the string
'''

def trysplitting_dash(valuesstring):
    valueslist = valuesstring.split(' ')
    if len(valueslist):
        keepgoing = 0
        for value in range(len(valueslist)):
            if valueslist[keepgoing] == '-' or valueslist[keepgoing] == '–':
                break
            else:
                keepgoing += 1
        if keepgoing == len(valueslist):
            splitresult = 'FLAG'
        elif len(valueslist) > keepgoing > 2:
            leftvalue = ' '.join(valuesstring.split(' ')[:keepgoing])
            rightvalue = ' '.join(valuesstring.split(' ')[keepgoing + 1:])
            splitresult = [leftvalue,rightvalue]
        else:
            splitresult = 'FLAG'
        return splitresult        
    else:
        return 'None'
    

def trysplitting_caps(valuesstring):
    valueslist = valuesstring.split(' ')
    if len(valueslist):
        wordindex = 0
        for word in valueslist:
            valueslist[wordindex] = re.sub(r'[^a-z]','', word, flags = re.IGNORECASE)
            wordindex += 1
        keepgoing = 0
        for value in range(len(valueslist)):
            if valueslist[keepgoing].isupper() or not valueslist[keepgoing].isalpha():
                keepgoing += 1
            else:
                break
        if keepgoing == len(valueslist):
            splitresult = 'FLAG'
        elif keepgoing > 2:
            leftvalue = ' '.join(valuesstring.split(' ')[:keepgoing])
            rightvalue = ' '.join(valuesstring.split(' ')[keepgoing:])
            splitresult = [leftvalue,rightvalue]
        else:
            splitresult = 'FLAG'
        return splitresult

def tryextracting(valuesstring):
    extraction = trysplitting_caps(valuesstring)
    if extraction == 'FLAG':
        if trysplitting_dash(valuesstring) != 'FLAG':
            return trysplitting_dash(valuesstring)[0]
        else:
            return 'FLAG'
    else:
        return extraction[0]


'''
Fills in the "Type" column with the appropriate regulation by identifying flag words (ex. tow-away, red zone, RPP)
'''

'''
regulations = ['COLOR CURB','TIME LIMIT','METER','ANGLED PARKING','RPP','TOW-AWAY NO STOPPING','TOW-AWAY NO PARKING']

def identify_colorcurb(regulationstring):
    colorcurbflag = r'white%zone|blue%zone|green%zone|red%zone|%curb%'
    match = re.findall(regulationstring, colorcurbflag ,re.IGNORECASE)
    if match:
        return match
    else:
        return None

def identifier(regulationstring):
    regulationtype = 'CHECK'
    return regulationtype
'''    

'''
This function takes all the above functions and runs them sequentially
'''

def reg_rowmaker_v1(dataframe, indexnum):
    reg_row = []
    # Motion
    reg_row.append(backtrack(indexnum, dataframe, 0))
    # Date
    reg_row.append(backtrack(indexnum, dataframe, 1))
    # Regulation
    if dataframe.iloc[indexnum, 0] == None:
        reg_row.append(None)
    else:
        reg_row.append(tryextracting(dataframe.iloc[indexnum, 4]))
    # Type
    reg_row.append(dataframe.iloc[indexnum, 3])
    # Text
    reg_row.append(dataframe.iloc[indexnum, 4])
    # Block and Street
    reg_row.append(dataframe.iloc[indexnum, 5])
    return reg_row

'''
Exporting data to a dictionary
'''

unknownonlydictionary = {}
for i in range(len(unknownonlyregulations)):
    unknownonlydictionary[i] = reg_rowmaker_v1(unknownonlyregulations, i) 


finalunknownonly0 = pd.DataFrame.from_dict(unknownonlydictionary, orient = 'index')
finalunknownonly = finalunknownonly0.rename(columns={0 :'Motion', 1:'Date', 2:'Regulation', 3:'Type', 4:'Text',
                                                  5: 'Block and Street'})

Location2 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\MTAB_ParkingResolutions_2002_to_2015_JP_V00.xlsx'
finalunknownonly.to_excel(Location2, sheet_name = 'UnknownOnly', engine = 'xlsxwriter', index = False)