import numpy as np


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
    
    MetComputeLatitudeMin=-66.5
    MetComputeLatitudeMax=66.5
    #The PEVT and disaggregation calculations are valid for this range 
    #of Latitude and Longitude only.
    if aLatDeg < MetComputeLatitudeMin or aLatDeg > MetComputeLatitudeMax: #invalid latitude 
        print('Latitude value is not within range!')
        return -999
        
    else: #latitude ok,convert to radians
        
        JulDay = 30.5 * (aMonth - 1) + aDay
        LatRdn = np.radians(aLatDeg)
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
