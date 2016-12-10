# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 17:42:55 2016

@author: AZhang1
"""

import pandas as pd
import re

Location1 = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\Parsed_Resolutions_v1\Testplacement\752_resolutions_testparse.xlsx'

metertestparse = pd.read_excel(Location1, header = 0)

metertextlist = list(metertestparse.loc[:,'Text'])

def streetnamefinder(textchunk):
    match = re.findall(sfstreetnames,textchunk, re.IGNORECASE)
    if match:
        return match
    else:
        return []
        
def intersectionparser(listchunks):
    if len(listchunks) == 2:
        return ' & '.join(listchunks)
    elif len(listchunks) == 0:
        return 'FLAG'
    else:
        for item in listchunks:
            if item in sfstreetnames


Locationfinal = r'L:\GIS\Projects\ParkingRegulations\DATA\MTA Board Resolutions\Parsed_Resolutions_v1\Testplacement\meter_testparse.xlsx'

meterdict = {}
for ij in range(len(metertextlist)):
    meterdict[ij] = metertextlist[ij]   

meter_dfprocess = pd.DataFrame.from_dict(meterdict, orient = 'index')
meter_dfprocess.to_excel(Locationfinal, sheet_name = 'Sheet1', engine = 'xlsxwriter', index = True)