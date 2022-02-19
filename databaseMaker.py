#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os 
import re
import pandas as pd
import re
import numpy as np


# In[5]:


# Helper method for create().
# True if can be cast to a float
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
# Read in data and names file.
# files must have the format
# Results_<date>_<sweep>_<pulse pairs>.xls
# names_<date>_<sweep>_<pulse pairs>.xlsx

def create():
    datDict, backDict = {}, {}
    patDat= re.compile(r'Results_(?P<date>\d+)_(?P<sweep>\w+)_(?P<ppairs>\d+)\.xls')
    path = os.path.join(os.getcwd(),'ARP data/')
    
    # iterate through the directories
    for item in os.listdir(path):
        for f in os.listdir(os.path.join(path,item)):
            m = patDat.match(f)
            p = os.path.join(path,item+'/')
            if m:     
                # read files
                df=pd.read_csv(p+f, sep='\t')
                cols = pd.read_excel(p+'names_'+m.group('date')+'_'+m.group('sweep')+'_'+m.group('ppairs')+'.xlsx',engine="openpyxl")
                
                # rename columns to their image number
                cols=cols[cols.columns[0]]
                cols = pd.DataFrame(np.insert(cols.values, 0, values=[cols.name], axis=0))
                cols.rename(columns = {cols.columns[0]:'detuning'},inplace = True)
                df.drop(columns=[' ','x'], inplace=True)
                df.columns = [re.search('\d+',x).group() for x in df.columns]
                
                # save background images in separate dictionary
#                 try:
#                     backDict[m.group('sweep')][m.group('ppairs')]=df[df.columns[4]]
#                     print(df.columns[4])

#                 except:
#                     backDict[m.group('sweep')]={}
#                     backDict[m.group('sweep')][m.group('ppairs')]=df[df.columns[4]]
#                     print(df.columns[4])

                # drop bad frames and other non-data
                
                todrop = [cols.index[cols['detuning']==x].tolist() for x in cols['detuning'] if not is_number(x)]
                dropped = set()
                for li in todrop:
                    for val in li:
                        dropped.add(str(val+1))
                df.drop(columns = list(dropped), inplace=True)

                # rename columns to their detuning amount
                cols.drop(index = [int(x)-1 for x in list(dropped)],inplace=True)
                cols['detuning']=cols['detuning'].astype(int)
                cols.sort_values(by='detuning',inplace=True)
                cols['x']=cols.index+1
                df = df.reindex(columns=[str(i) for i in list(cols['x'])])
                df.columns = cols['detuning']
                df
                try:
                    datDict[m.group('sweep')][m.group('ppairs')]=df

                except:
                    datDict[m.group('sweep')]={}
                    datDict[m.group('sweep')][m.group('ppairs')]=df

    # exceptions:300 upup(averaged hgh oscs)
    
    # 100 upup 
    df = datDict['upup']['100']
    parts = [df[df.columns[:24]],df[df.columns[25:29]]-.8,df[df.columns[30:]]]
    datDict['upup']['100']=pd.concat(parts, axis=1)
    return datDict, backDict


# In[ ]:




