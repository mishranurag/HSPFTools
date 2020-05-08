# -*- coding: utf-8 -*-
"""
Created on April 7, 2020

This script imports timeseries data saved in a CSV file
and fills the gaps using nearby stations or interpolation.

If the imported data includes air temperature, then it also 
calculates daily potential evapotranspiration using Hamon method,
and then disaggregates it to hourly values.

@author: Anurag Mishra
"""

import numpy as np
import pandas as pd
from wdmtoolbox import wdmtoolbox as wdm

MetComputeLatitudeMin=-66.5
MetComputeLatitudeMax=66.5
#The PEVT and disaggregation calculations are valid for this range 
#of Latitude and Longitude only.

DegreesToRadians=0.01745329252

def PanEvaporationValueComputedByHamon(aTAVC, aMonth, aDay, 
                                       aLatDeg, aDegF):
    '''
    This function is adapted from BASINS code. It takes a value or a timeseries
    of daily average temperature as input, and calculates daily potential 
    evapotranspiration using Hamon Method.
    To understand the mathematical basis for this calculation, please
    refer to BASINS documentation.
    
    :param float aTAVC: Average air temperature value or series in degF or degC
    :param integer aMonth: Month of the year
    :param integer aDay: Day of the month
    :param float aLatDeg: Latitude of the loation in Degrees
    :param float aDegF: True if temperature is in degF, False if in degC
    '''
    if aLatDeg < MetComputeLatitudeMin or aLatDeg > MetComputeLatitudeMax: #invalid latitude 
        print('Latitude value is not within range!')
        return -999
        
    else: #latitude ok,convert to radians
        
        JulDay = 30.5 * (aMonth - 1) + aDay
        LatRdn = aLatDeg * DegreesToRadians
        Phi = LatRdn
        AD = 0.40928 * np.cos(0.0172141 * (172.0 - JulDay))
        SS = np.sin(Phi) * np.sin(AD)
        CS = np.cos(Phi) * np.cos(AD)
        X2 = -SS / CS
        Delt = 7.6394 * (1.5708 - np.arctan(X2 / np.sqrt(1.0 - np.power(X2,2))))
        SunR = 12.0 - Delt / 2.0
        SUNS = 12.0 + Delt / 2.0
        DYL  = (SUNS - SunR) / 12

        #convert temperature to degC, if necessary
        if aDegF: aTAVC = (aTAVC - 32.0) * (5.0 / 9.0)

        #Hamon equation
        VPSAT = 6.108 * np.exp(17.26939 * aTAVC / (aTAVC + 237.3))
        VDSAT = 216.7 * VPSAT / (aTAVC + 273.3)
        
        aCTS=np.where(aMonth>0,0.0055,0)
        #make aCTS as a series based on aMonth
        #The BASINS applications I have seen all use the value of 0.0055
        #for all the months
        
        lPanEvap = aCTS * DYL * DYL * VDSAT
        #when the estimated pan evaporation is negative
        #the value is set to zero
        lPanEvap.where(lPanEvap<0,0)
        
        return lPanEvap


def PETDST(aDayPet, aLatDeg, aMonth, aDay):

    ''' This function is adapted from BASINS code. It takes a value of daily 
    potential evapotranspiration and outputs a list of 24 values for the 
    day.
    To understand the mathematical basis for this calculation, please
    refer to BASINS documentation.
    
    :param float aDayPet: Average PET in inches
    :param float aLatDeg: Latitude of the loation in Degrees
    :param integer aMonth: Month of the year
    :param integer aDay: Day of the month 
    '''

    #julian date
    JulDay = 30.5 * (aMonth - 1) + aDay
    
    #check latitude
    if aLatDeg < MetComputeLatitudeMin or \
        aLatDeg > MetComputeLatitudeMax: #invalid latitude, return
        aRetCod = -1
        print(aRetCod)
    else: #latitude ok
        #convert to radians
        LatRdn = aLatDeg * DegreesToRadians

        Phi = LatRdn
        AD = 0.40928 * np.cos(0.0172141 * (172.0 - JulDay))
        SS = np.sin(Phi) * np.sin(AD)
        CS = np.cos(Phi) * np.cos(AD)
        X2 = -SS / CS
        Delt = 7.6394 * (1.5708 - np.arctan(X2 / np.sqrt(1.0 - np.power(X2,2))))
        SunR = 12.0 - Delt / 2.0

        #develop hourly distribution given sunrise,
        #sunset and length of day (DELT)
        DTR2 = Delt / 2.0
        DTR4 = Delt / 4.0
        CRAD = 0.66666667 / DTR2
        SL = CRAD / DTR4
        TRise = SunR
        TR2 = TRise + DTR4
        TR3 = TR2 + DTR2
        TR4 = TR3 + DTR4
        aHrPET=24*[0]
        CURVE=24*[0]
        #calculate hourly distribution curve
        for IK in range(24):
            #print(IK)
            RK = IK
            if RK > TRise:
                if RK > TR2:
                    if RK > TR3:
                        if RK > TR4:
                            CURVE[IK] = 0.0
                            aHrPET[IK]=CURVE[IK]
                        else:
                            CURVE[IK] = (CRAD - (RK - TR3) * SL)
                            aHrPET[IK] = CURVE[IK] * aDayPet
                    else:
                        CURVE[IK] = CRAD
                        aHrPET[IK] = CURVE[IK] * aDayPet
                else:
                    CURVE[IK] = (RK - TRise) * SL
                    aHrPET[IK] = CURVE[IK] * aDayPet
            else:
                CURVE[IK] = 0.0
                aHrPET[IK] = CURVE[IK]
            #print('aHRPET Value', IK, aHrPET[IK])
            #print('CURVE Value', IK, CURVE[IK])
            if aHrPET[IK] > 40:
                print("Bad Hourly Value ", aHrPET[IK])
            

    return aHrPET

wdmpath='Test.wdm'
#Download it here
#https://www.dropbox.com/s/sl6njhiym8d2yb1/Test.wdm?dl=0

ListOfATEMDSN=[[1,'BSprings',33.93]]
#A list of list of DSN, station name, and latitude

for key,Location,Latitude in ListOfATEMDSN:
    #Going through a list DSN with location, and latitude values
    df=wdm.extract(wdmpath,key)
    #Extracting the dataset from wdmfile
    df=df.resample('D').mean()
    #Calculatinf average daily temperature
    df=df.apply(lambda x: PanEvaporationValueComputedByHamon(x,x.index.month,
                                                         x.index.day,
                                                        Latitude,True))
    #Using lambda to calculate daily potential evapotranspiration
    DSN=key+1000
    #Providing a random DSN for new Timeseries of Daily EVAP
    
    wdm.createnewdsn(wdmpath,dsn=DSN,tstype='EVAP',base_year=2000,
                 tcode=4,statid=Location[0:15],scenario='COMPUTED',
                 location=Location[0:7],constituent='EVAP', tsfill=-999,
                 description='Daily Potential Evap Using Hamon')
        #saving the daily PET in the WDM file
    wdm.csvtowdm(wdmpath=wdmpath,
                     dsn=DSN,
                     input_ts=df)
    
    ser=pd.Series()
    #creating empty timeseries
    for eachday,value in df.iterrows():
        #going through each day in the daily PET timeseries
        HourlyValues=PETDST(value[0], Latitude, eachday.month, eachday.day)
        #Calculating hourly PET values based on the PETDST function
        
        ts=pd.Series(HourlyValues,index=pd.date_range(eachday, 
                                                      periods=24, freq='H'))
        #Making a hourly timeseries for the day for which PET is calculated
        
        if len(ser)==0:
            ser=ts
        else:
            ser=ser.append(ts)
    
    DSN=key+2000
    #Providing a random DSN for new Timeseries of Hourly Evap
    wdm.createnewdsn(wdmpath,dsn=DSN,tstype='PEVT',base_year=2000,
                 tcode=3,statid=Location[0:15],scenario='COMPUTED',
                 location=Location[0:7],constituent='PEVT`', tsfill=-999,
                 description='Hourly PEVT From Disaggregated Hamon')   
    
        
    wdm.csvtowdm(wdmpath=wdmpath,
                     dsn=DSN,
                     input_ts=ser)