
''' This program gives the start and end times of tail currents (in ms) a specified protocol.

    protocolname = name of protocol used, in string format (Henckels, Okada, BradleyLong, BradleyShort, AndyLam)
    enter i=0 for second argument if not Okada Ca dependent - enter i=n for Okada, where n is the sweep number of interest


    Created by: Sayaka (Saya) Minegishi
    Contact: minegishis@brandeis.edu
    Last modified: Jun 19 2024
'''


def getStartEndTail(protocolname,i):
    if protocolname == "Henckels":
        startTail = 0.5811
        endTail = 0.6312
    
    elif protocolname == "BradleyLong":

        startTail =0.5970
        endTail = 1.5975
    elif protocolname == "Okada":
        startTail=0.1124
        endTail = i * 0.102 + 0.1124

    # elif protocolname == "AndyLam":
    #     startTail =0.5970
    #     endTail = 1.5975
    #TODO: add andylam and bradleyshort

    return startTail, endTail

