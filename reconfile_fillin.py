# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:33:54 2016

@author: AZhang1
"""

import pandas as pd

Location1 = r'L:\GIS\Projects\ParkingRegulations\Meter_reg_reconciliation\Copy of ips sfmta inventory recon_20151021_1 (1) 12-24-15 (Final).xls'
reconfile0 = pd.read_excel(Location1, header = 0)

reconfile = reconfile0.where((pd.notnull(reconfile0)),None)

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

'''
This function takes all the above functions and runs them sequentially
'''


def columnfiller_v1(dataframe, indexnum):
    newrecon = []
    onlycolumn1 = list(range(0,5))
    onlycolumn2 = list(range(5,23))
    for column1 in onlycolumn1:    
        newrecon.append(backtrack(indexnum, dataframe, column1))
    for column2 in onlycolumn2:
        newrecon.append(dataframe.iloc[indexnum, column2])
    return newrecon
    
'''
Exporting data to a dictionary
'''

recondictionary = {}
for i in range(len(reconfile)):
    recondictionary[i] = columnfiller_v1(reconfile, i) 


finalrecon0 = pd.DataFrame.from_dict(recondictionary, orient = 'index')
finalrecon = finalrecon0.rename(columns={0 :'Street and Block', 1:'Post ID', 2:'Cap Color', 3:'Days of Week', 4:'Source',
                                                  5: 'Start Time', 6: 'End Time', 7: 'Rate', 8: 'TL', 9: 'Prepay/ Tow/ Free', 10: 'See Signs',
                                                  11: 'Comments', 12: 'Cross Street', 13: 'MTAB Resolution', 14: 'MTAB Motion', 15: 'Street and Block',
                                                  16: 'Motion Text', 17: 'motion_num', 18: 'date', 19: 'motion_type', 20: 'motiontext', 21: 'street',
                                                  22: 'street', 23: 'etc'})

Location2 = r'L:\GIS\Projects\ParkingRegulations\Meter_reg_reconciliation\IPS_SFMTA_inventory_recon_20151021_filledin.xlsx'
finalrecon.to_excel(Location2, sheet_name = 'UnknownOnly', engine = 'xlsxwriter', index = False)
