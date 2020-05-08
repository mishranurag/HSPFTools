'''This is an example script that finds all the DSN from a WDM file
and uses the first DSN to extract the data and plot it. 
It can easily be modified to loop through all the datasets.'''

from wdmtoolbox import wdmtoolbox as wdm
import pandas as pd
files_path='C:\BASINS45\modelout\Test'
wdmfile= os.path.join(files_path,'Test.wdm')
DataList=wdm.listdsns(wdmfile) #Getting the list of all datasets from the WDMFile as OrderedDict
DSNList=list(DataList.keys()) #Extracting the list of DSN from DataList
dataSeries=wdm.extract(wdmfile,DSNList[0]) #extracting the dataset using the first DSN in DSNList
dataSeries=dataSeries['2002-05-31':'2002-07-31'] #subsetting the data
dataSeries.plot() #plotting the dataframe
#dataSeries is a dataframe
