import numpy as np
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
    MetComputeLatitudeMin=-66.5
    MetComputeLatitudeMax=66.5
    #The PEVT and disaggregation calculations are valid for this range 
    #of Latitude and Longitude only.


    #julian date
    JulDay = 30.5 * (aMonth - 1) + aDay
    
    #check latitude
    if aLatDeg < MetComputeLatitudeMin or \
        aLatDeg > MetComputeLatitudeMax: #invalid latitude, return
        aRetCod = -1
        print(aRetCod)
    else: #latitude ok
        #convert to radians
        LatRdn = np.radians(aLatDeg)

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
