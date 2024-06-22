
''' This program gives the start and end times of tail currents (in ms) a specified protocol.

    protocolname = name of protocol used, in string format (Henckels, Okada_dep, Okada_tail, BradleyLong, BradleyShort, AndyLam)
    enter i=0 for second argument if not Okada Ca dependent - enter i=n for Okada, where n is the sweep number of interest

    startTail = end of hyperpolarizing pulse

    Created by: Sayaka (Saya) Minegishi
    Contact: minegishis@brandeis.edu
    Last modified: Jun 19 2024
'''
#TODO: modify so that tail current duration is the same for all protocols.


def getStartEndTail(protocolname,i):
    if protocolname == "Henckels":
        startTail = 0.5811
        endTail = 0.6312
    
    elif protocolname == "BradleyLong":

        startTail =0.5970
        endTail = 0.5970 + (0.6312-0.5811) #duration of tail same as Henckels to keep everything consistent
        #endTail = 1.5975 - from original protocol

    elif protocolname == "Okada_dep":
        #gives depolarization start and end times
        startTail=0.1124 #start of depolarization
        endTail = i * 0.102 + 0.1124 #end of depolarization

    elif protocolname == "Okada_tail":
        #gives tail current start and end times for each sweep

        if i == 1:
            startTail = 0.2126
        elif i==2:
            startTail = 0.3123
        
        elif i == 3:

            startTail = 0.4121
        elif i == 4:
            startTail =0.5125
        elif i == 5:
            startTail = 0.6123

        elif i == 6:
            startTail =0.7123
        elif i == 7:
            startTail =0.8128
        elif i == 8:
            startTail =0.9127
       
            
        endTail =  startTail+ 0.6312 - 0.5811 #same as Henckels

    # elif protocolname == "AndyLam":
    #     startTail =0.5970
    #     endTail = 1.5975
    #TODO: add andylam and bradleyshort

    return startTail, endTail


#return the last sweeep number for the given protocol
def get_last_sweep_number(protocolname):
    if protocolname == "Henckels":
        lastsweep = 10
    
    elif protocolname == "BradleyLong":

        lastsweep = 10
    elif protocolname == "Okada_dep":
        lastsweep = 7
    elif protocolname == "Okada_tail":
        lastsweep = 7

    elif protocolname == "Okada":
        lastsweep = 7
    elif protocolname == "BradleyShort":

        lastsweep = 10
    
    return lastsweep



''' This program gives the start and end times of tail currents (in ms) a specified protocol.

    protocolname = name of protocol used, in string format (Henckels, Okada_dep, Okada_tail, BradleyLong, BradleyShort, AndyLam)
    enter i=0 for second argument if not Okada Ca dependent - enter i=n for Okada, where n is the sweep number of interest

    startTail = end of hyperpolarizing pulse

    Created by: Sayaka (Saya) Minegishi
    Contact: minegishis@brandeis.edu
    Last modified: Jun 19 2024
'''
#TODO: modify so that tail current duration is the same for all protocols.


def getStartEndTail(protocolname,i):
    if protocolname == "Henckels":
        startTail = 0.5811
        endTail = 0.6312
    
    elif protocolname == "BradleyLong":

        startTail =0.5970
        endTail = 0.5970 + (0.6312-0.5811) #duration of tail same as Henckels to keep everything consistent
        #endTail = 1.5975 - from original protocol

    elif protocolname == "Okada_dep":
        #gives depolarization start and end times
        startTail=0.1124 #start of depolarization
        endTail = i * 0.102 + 0.1124 #end of depolarization

    elif protocolname == "Okada_tail":
        #gives tail current start and end times for each sweep

        if i == 1:
            startTail = 0.2126
        elif i==2:
            startTail = 0.3123
        
        elif i == 3:

            startTail = 0.4121
        elif i == 4:
            startTail =0.5125
        elif i == 5:
            startTail = 0.6123

        elif i == 6:
            startTail =0.7123
        elif i == 7:
            startTail =0.8128
        elif i == 8:
            startTail =0.9127
       
            
        endTail =  startTail+ 0.6312 - 0.5811 #same as Henckels

    # elif protocolname == "AndyLam":
    #     startTail =0.5970
    #     endTail = 1.5975
    #TODO: add andylam and bradleyshort

    return startTail, endTail


#return the last sweeep number for the given protocol
def get_last_sweep_number(protocolname):
    if protocolname == "Henckels":
        lastsweep = 10
    
    elif protocolname == "BradleyLong":

        lastsweep = 10
    elif protocolname == "Okada_dep":
        lastsweep = 7
    elif protocolname == "Okada_tail":
        lastsweep = 7

    elif protocolname == "Okada":
        lastsweep = 7
    elif protocolname == "BradleyShort":

        lastsweep = 10
    
    return lastsweep


#get depolarization start and end times
def getDepolarizationStartEnd(protocolname):
    if protocolname == "Henckels":
        startdep = 0.0811
        enddep = 0.5811
    
    elif protocolname == "BradleyLong":

        startdep = 0.0962
        enddep = 0.5969

    # elif protocolname == "BradleyShort":
    #     #TODO: ENTER STUFF

    return startdep, enddep



  