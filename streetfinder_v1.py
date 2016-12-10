# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:23:11 2016

@author: AZhang1
"""

import pandas as pd
import re
import string

# Reading the San Francisco Street Name File
Location2 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\Scripts\Supportingfiles\San_Francisco_Street_Names.csv'
streetname_df = pd.read_csv(Location2)

# Reading the USPS Suffix List File
Location3 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\Scripts\Supportingfiles\USPS_Street_Suffixes.xlsx'
df_suffx0 = pd.read_excel(Location3, header = None, skiprows = [0,1,2,3])
# Rename all the columns to their proper name. 
df_suffx = df_suffx0.rename(columns={0 : 'Primary Street Suffix Name', 
                                     1 : 'Commonly Used Street Suffix or Abbreviation', 
                                     2 : 'Postal Service Standard Suffix Abbrevation'})

def find_matching_suffixes(stringtest,listofstreets):
    acceptedstreetsuffixes = r'\b' + r'\b|\b'.join(listofstreets)
    match = re.findall(acceptedstreetsuffixes,stringtest,re.IGNORECASE)
    if match:
        if len(match) > 1:
            return set(match)
        else:
            return set(match.group())
    else:
        return None
    
def preceding_street(stringtest, suffx_l):
    matchedstreet = find_matching_suffixes(stringtest,suffx_l)
    if matchedstreet == None:
        return None
    else:
        returnedstreets = []
        for matchedsuffx in matchedstreet:
            suffxstring = r'(\w+\s)?\b([\w]+)\s(?=' + matchedsuffx + r'\b)'
#            suffxstring = r'([\w]+)\s([\w]+)\s(\b' + matchedsuffx + r'\b)'
            matchstreet = re.findall(suffxstring,stringtest,re.IGNORECASE)
            returnedstreets.extend(matchstreet)
        returnedstreets2 = []
        for value in returnedstreets:
            returnedstreets2.append(value)
        return returnedstreets2
        
def longwordstreet(streetname):
    if len(' '.split(streetname)) >= 3:
        return streetname

threewordsplusstreets = list(streetname_df.loc[:,'StreetName'])


'''
def findstreetsinstring(search_string):
    allstreets = []
    # First, find if there's a really long street.
    match = re.findall(threewordsplusstreets, search_string, re.IGNORECASE)
    if match:
        allstreets.extend(match)
    # Then find the words prefacing those suffixes
    normalstreets = preceding_street(search_string,full_suffixeslist)
    allstreets.extend(normalstreets)
    # Check to see if those words are streets 
    for item in normalstreets:
        item2 = ' '.join(item[0],item[1])
        if item2 in sfstreetnames:
            allstreets.extend(' '.join(item))
        elif item[1] in sfstreetnames:
            allstreets.extend(' '.join(item[1],item[2]))
    return allstreets
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

extractedstreets_dict = {}
for i in range(len(unknownonlyregulations)):
    extractedstreets_dict[i] = reg_rowmaker_v1(unknownonlyregulations, i) 


finalextractedstreets0 = pd.DataFrame.from_dict(extractedstreets_dict, orient = 'index')
finalextractedstreets = finalextractedstreets0.rename(columns={0 :'Motion', 1:'Date', 2:'Regulation', 3:'Type', 4:'Text',
                                                  5: 'Block and Street'})

Location2 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\MTAB_ParkingResolutions_2002_to_2015_JP_V00.xlsx'
finalextractedstreets.to_excel(Location2, sheet_name = 'ExtractedStreets', engine = 'xlsxwriter', index = False)