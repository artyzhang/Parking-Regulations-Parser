# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 16:29:57 2015

@author: artyz
python version 3.4.3
pandas version 17.0
"""

import pandas as pd
import re
import string


'''
Section 1: Importing the necessary documents

MTAB_df: The dataframe with all the resolution values.
df_suffx: A dataframe with all of the USPS suffixes.

Note that all the file locations are incorrect.
'''
# Preparing the actual MTA Board Resolution File
# Read the excel file

Locationyear = str(input('Year?  '))
Location1 = r'C:\Users\artyz\Desktop\MTAB Convert_firstround\Direct Export' + r'\MTAB_Parking Resolutions_' + Locationyear + r'.xlsx'
Locationfinal = r'C:\Users\artyz\Desktop\MTAB Convert_firstround' + r'\MTAB_Parking_Resolutions_processed_' + Locationyear + r'.xlsx'
MTAB_df0 = pd.read_excel(Location1, header = None)
# Convert all data to strings
MTAB_df0[MTAB_df0.columns[1]] = MTAB_df0[MTAB_df0.columns[1]].apply(str)
# Rename the three columns
MTAB_df00 = MTAB_df0.rename(columns={0 : 'Motion', 1 : 'Date', 2 : 'Text'})
# Replace np.NaN with None, so that it satisfies booleans.
MTAB_df = MTAB_df00.where((pd.notnull(MTAB_df00)),None)
# Replace np.NaT with None, so that it satisfies booleans
MTAB_df = MTAB_df.where(MTAB_df != 'NaT', None)
# Delete all 
MTAB_df = MTAB_df.dropna(subset = ['Text'])

# Reading the San Francisco Street Name File
Location2 = r'C:\Temp_GIS\MTAB_Spot_Checking\02_OtherData\San_Francisco_Street_Names.xls'
streetname_df = pd.read_excel(Location2)

# Reading the USPS Suffix List File
Location3 = r'C:/Temp_GIS/MTAB_Spot_Checking/02_OtherData/USPS_suffixes.xlsx'          
df_suffx0 = pd.read_excel(Location3, header = None, skiprows = [0,1,2,3])
# Rename all the columns to their proper name. 
df_suffx = df_suffx0.rename(columns={0 : 'Primary Street Suffix Name', 
                                     1 : 'Commonly Used Street Suffix or Abbreviation', 
                                     2 : 'Postal Service Standard Suffix Abbrevation'})
# Convert NaN columns to None. 
df_suffx = df_suffx.where((pd.notnull(df_suffx)),None)

'''
Section 2: Preliminary functions. 
'''

def doubleletter(x):
    try:
        x = int(x)
    except ValueError:
        return
    alphabet = list(string.ascii_uppercase)
    all_list = []
    i = 1
    while i <= x:
        templist = []
        for letter in alphabet:
            templist.append(letter*i)
        all_list.extend(templist)
        i += 1
    return all_list

def trim(str_list):
    index = 0
    for item in str_list:
        str_list[index] = item.strip()
        index += 1
    return str_list

def backtrack(indexnum, data_frame, column_num):
    dateormotion = data_frame.iloc[indexnum,column_num]
    if dateormotion == None or str(dateormotion) == 'NaT':
        indexnum = indexnum - 1
        return backtrack(indexnum, data_frame, column_num)
    else:
        return dateormotion

def backtrackreplace(dataframe, column_num):
    index = 0
    for item in dataframe.iloc[:, column_num]:
        dataframe.iloc[index,column_num] = backtrack(index,dataframe, column_num)
        index += 1
    return dataframe

def removefromstring(stringlist, itemtoremove, typeof):
    stringlist2 = stringlist.split()
    if typeof == 'motionletter':
        letter = itemtoremove + '.'
        if letter in stringlist2:
            stringlist2.remove(letter)
        return ' '.join(stringlist2)
    elif typeof == 'establish_revoke':
        if itemtoremove in stringlist2:
            stringlist2.remove(itemtoremove)
        if stringlist2[0] == '-':
            stringlist2.remove[0]            
        return ' '.join(stringlist2)
    else:
        return stringlist

'''
Section 3: Preparing lists that will be used for following functions.

possiblemotionletters: [A,B,C,D,...AA,BB,CC,DD...AAA,BBB,CCC,DDD...]
sfstreetnames: All streets in San Francisco.
full_suffixeslist: All suffixes and their abbreviations.
longsfstreetnames = All streets in San Francisco longer than three words.
threewordsplusstreets: for regex findall function, find all these long streets.

'''
# Creating a list of uppercase alphas for motion letter finding. 
possiblemotionletters = doubleletter(4)

# Creates a list of all street names 
sfstreetnames = []
for item in streetname_df['StreetName']:
    sfstreetnames.append(item)
longstreetstring = r'\b'+ r'\b|\b'.join(sfstreetnames) + r'\b'

df_suffx = backtrackreplace(df_suffx,0)

# Isolate all the street names longer than two words.
morethantwowords = []
twowordindex = 0
for item in sfstreetnames:
    if len(item.split(' ')) > 2:
        morethantwowords.append(twowordindex)
        twowordindex += 1
    else:
        twowordindex += 1
longsfstreetnames = []        
for item in morethantwowords:
    longsfstreetnames.append(sfstreetnames[item])
threewordsplusstreets = '|'.join(longsfstreetnames)

# Create a list of USPS suffixes
df_suffx = backtrackreplace(df_suffx,2)
full_suffixeslist = set()   
for item in df_suffx.iloc[:,1]:  
    full_suffixeslist.add(item)

'''
Section 4: Actual workhorse functions
'''
# Extracts motion letter by checking the first '.' separated value in the list. 
def extract_motionletter(stringlist, letters):
    if stringlist == None:
        return 'Error'
    stringlist2 = stringlist.split('.')
    trim(stringlist2)
    if stringlist2[0] in letters:
        return stringlist2[0]
    else:
        return 'n/a'

# Extracts the Establish/Revoke through regular expressions.
def findall_establishrevoke(teststring):
    establishrevoke= ['ESTABLISH', 'RESCIND', 'REVOKE', 'EXTEND']
    establishrevoke = '|'.join(establishrevoke)
    match = re.findall(establishrevoke, teststring,re.IGNORECASE)
    if match:
        if len(match) > 1:
            return ', '.join(match)
        else:
            return match
    else:
        return 'n/a'
    
# Tries to split the string by iterating .isupper(): ALL CAPS ON ONE SIDE, the rest of them on the other side.


def trysplitting(valuesstring):
    valueslist = valuesstring.split(' ')
    if len(valueslist):
        wordindex = 0
        for word in valueslist:
            valueslist[wordindex] = re.sub(r'[^a-z]','', word, flags = re.IGNORECASE)
            wordindex += 1
        keepgoing = 0
        while valueslist[keepgoing].isupper() or not valueslist[keepgoing].isalpha():
            keepgoing += 1
            if keepgoing >= len(valueslist):
                return ' '.join(valuesstring.split(' ')[:keepgoing])
        if keepgoing < 2:
            return valuesstring
        else:
            leftvalue = ' '.join(valuesstring.split(' ')[:keepgoing])
            rightvalue = ' '.join(valuesstring.split(' ')[keepgoing:])
        return [leftvalue,rightvalue]

def endnumbercheck(twovalueslist):
    if len(twovalueslist ) != 2:
        return 'Not split'
    else:
        stringvalue1 = twovalueslist[0].split(' ')
        stringvalue2 = twovalueslist[1].split(' ')
        if stringvalue1[-1] == '-':
            del stringvalue1[-1]
            return endnumbercheck([' '.join(stringvalue1),' '.join(stringvalue2)])
        elif not stringvalue1[-1].isalpha():
            stringvalue2.insert(0,stringvalue1[-1])
            del stringvalue1[-1]
            return endnumbercheck([' '.join(stringvalue1),' '.join(stringvalue2)])
        else:
            return [' '.join(stringvalue1),' '.join(stringvalue2)]
            
def trysplitting_andcheck(valuestring):
    return endnumbercheck(trysplitting(valuestring))

def remove_extraneous(lst):
    extrasremoved = []
    extraneouslist = []
    mightbe = 0
    for value in lst:
        value = value.strip()
        if value in ['','and','from','of']:
            mightbe += 1
        else:
            extrasremoved.append(mightbe)
            mightbe += 1
    for valuee in extrasremoved:
        extraneouslist.append(lst[valuee].strip())
    return extraneouslist
    
# The following functions try to find a street suffix, then return the name of the street
# attached to the suffix.
def longstreetnames(stringtest):
    match = re.findall(longstreetstring, stringtest, re.IGNORECASE)
    if match:
        return match
    else:
        return None

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
            returnedstreets2.append(remove_extraneous(value))
        return returnedstreets2
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
    

'''
Section 5: Testing Grounds
'''

##test_stringindex = 0
##test_string = MTAB_df.iloc[test_stringindex,2]
##print(test_string)
##extract_motionletter(test_string,)
##findall_establishrevoke()
##trysplittingtest = trysplitting(test_string)
##print(trysplitting(test_string))
##print(endnumbercheck(trysplittingtest))

##longstreetnames()
##find_matching_suffixes()
##remove_extraneous()
##preceding_street()
##print(longstreetnames(test_string))


'''
Section 6: Putting the functions to work
'''

# For each item in MTAB_df.iloc[:,2], iterate this function over each string.
def spotchecking_rowmaker(dataframe, indexnum):
    dataframe = backtrackreplace(dataframe,0)
    dataframe = backtrackreplace(dataframe, 1)
    string = dataframe.iloc[indexnum,2]
    # Create list containing column values
    roughlist = []
    # First Column = Index (just for this date though, since we're processing these all separately)
    roughlist.append(indexnum)
    # Second Column = Motion
    roughlist.append(dataframe.iloc[indexnum,0])
    # Third Column = Date of motion
    roughlist.append(dataframe.iloc[indexnum,1])
    # Fourth Column = Motion letter
    motionletter = extract_motionletter(string, possiblemotionletters)
    roughlist.append(motionletter)
    # Fifth Column = Establish/Revoke
    estabrevoke = findall_establishrevoke(string)
    roughlist.append(estabrevoke)
    # Sixth Column = Resolution Type    
    if len(trysplitting(string)) == 2:
        roughlist.append(trysplitting(string)[0])
    else:
        roughlist.append('Not in capitalized format')
    # Seventh Column = Intersection
    roughlist.append(longstreetnames(string))
    # Eighth Column = Resolution Location
    if len(trysplitting(string)) == 2:
        roughlist.append(trysplitting(string)[1])
    else:
        roughlist.append('n/a')
    # Ninth Column = Full Motion Text
    roughlist.append(str(string))
    return roughlist

# A list of rows - each item in this list is another list, corresponding 
# to a row of data. 
dataframedict_list = []
# Let's see if this works
for i in range(len(MTAB_df)):
    dataframedict_list.append(spotchecking_rowmaker(MTAB_df, i))

def extendrows(textstring):
    textstring.split(';')
    return textstring
    
'''
Section 7: Creating the actual Row-Key Indexed Dictionary
'''
dataframedict = {}
for ij in range(len(dataframedict_list)):
    dataframedict[ij] = dataframedict_list[ij]   

'''
Section 8: Creating the DataFrame and excel sheet.
'''

MTAB_dfprocess = pd.DataFrame.from_dict(dataframedict, orient = 'index')
MTAB_dfprocess = MTAB_dfprocess.rename(columns={0 :'Index',1:'Motion', 2:'Date',3:'Motion Letter',4:'Establish/Revoke',5:'Resolution Type',6:'Intersection', 7:'Resolution Location',8:'Text'})

MTAB_dfprocess.to_excel(Locationfinal, sheet_name = 'Sheet1', engine = 'xlsxwriter', index = False)


