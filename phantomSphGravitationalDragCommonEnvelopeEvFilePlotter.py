from collections import OrderedDict
import csv
import re
import matplotlib.pyplot as plt

#Allows the user to select what files they want to open.
def openFiles():
    openedFiles=[]
    fileNames=[]
    
    while(True):
        print("Type the path of a file to open. Enter f if finished selecting files.")
        filePath=input()
        
        if(filePath=="f"):
            return fileNames,openedFiles #The user has finished selecting the files to be opened.
    
        fileNames.append(filePath)
        openedFiles.append(open(file=filePath,mode="r"))


#Associates column names, column data and the file they came from with a key that allows the selection of columns to plot in getColumnPairsToPlot.
def getColumnData(fileNames,openedFiles):
    columnData=OrderedDict() #An ordered dictionary that associates a key to information (also a dictionary) about each column. As the ordered dictionary
    #iterates items the order they are added to the dictionary and that columns from the same file are added to the dictionary together (as seen below), columns
    #are grouped together based on what file they came from making information about the columns easier to read in getColumnPairsToPlot.
    
    for i,cfnCf in enumerate(zip(fileNames,openedFiles)):
        currentFileName=cfnCf[0]
        currentFile=cfnCf[1]
        
        firstLine=currentFile.readline()
        currentFile.seek(0) #The current read position in the opened file is reset.
        
        currentFileReader=csv.reader(currentFile,delimiter=" ",skipinitialspace=True)
        currentFileDataString=list(currentFileReader) #This list has string representations of the data.
        rowCount=len(currentFileDataString)
        columnCount=len(currentFileDataString[1])
        currentFileDataFloat=[[float(currentFileDataString[i][j]) for i in range(1,rowCount)] for j in range(columnCount)] #Stores the data in a float format instead
        #of a string format. Each sublist contains the values for a particular column. The first row is ignored because it contains the column names for the file.

        currentColumnTitles=re.findall("(?<=\[).{1,15}(?=\])",firstLine) #All substrings of the first line in the file with a length from 1 to 15 characters between a [ and a ] are found.    
        
        for j in currentColumnTitles: #Loops through all found column titles (column numbers and their names).
            columnNumber=re.search("(?<=^)( *)([0-9]+)",j) #Gets a sequence of numbers following the start of the string and possibly some spaces.
            columnName=re.search("(?<=^)( *[0-9]+ *)(.+)",j) #Gets the substring following the start of the string, possibly some spaces, a number and possibly some spaces.
            
            columnKey=columnNumber.group(2)
            columnDataIndex=int(columnKey)-1 #This number is shifted down by 1 because the column data list starts indices at zero while the numbers in the column titles start at 1.
            columnKeySuffix="" if(len(openedFiles)==1) else chr(ord("a")+i) #If there is more than 1 file, the key associated with the column information has a letter after the
            columnKey+=columnKeySuffix #number that changes depending on what file the column belongs to. The letters start with a and advance through the Unicode characters.
            
            currentColumnData={"fileName":currentFileName,"columnName":columnName.group(2),"values":currentFileDataFloat[columnDataIndex]}           
            columnData[columnKey]=currentColumnData #The key is associated with information about the column.

    return columnData
    

#Asks the user for an input; if the input is not in the allowed list the user is asked to try again.
def processAllowedUserInputs(allowedInputs):
    while(True):
        currentInput=input()
        
        if(currentInput in allowedInputs):
            return currentInput
        else:
            print("That input is invalid. Try again.")
        

        
def getColumnPairsToPlot(fileNames,columnData):
    curvesToPlot=[] #Holds a list of tuples containing the keys of the x and y column pairs to be plotted along with the desired legend name.
    
    allowedColumnIndices=[i for i in columnData.keys()]
    allowedColumnIndices.append("f") #The entry for choosing to stop selecting column pairs.
    
    previousFileName=""
    while(True):
        print("Select the x index, y index and desired legend name corresponding to what you want to plot. Enter f if you are finished with selecting columns to plot.")
    
        for currentKey,currentColumnData in columnData.items(): #Loops through all columns.
            currentFileName=currentColumnData["fileName"]
            currentColumnName=currentColumnData["columnName"]
            
            if(currentFileName!=previousFileName): #The file name is displayed if the current column is associated with a different file than the previous column.
                print(" "+currentFileName)
                previousFileName=currentFileName
                
            print("  "+currentKey+", "+currentColumnName)
        
        xIndexSelection=processAllowedUserInputs(allowedColumnIndices) 
        if(xIndexSelection=="f"):
            return curvesToPlot
        
        yIndexSelection=processAllowedUserInputs(allowedColumnIndices)
        if(yIndexSelection=="f"):
            return curvesToPlot
        
        desiredLegendName=input()
        if(desiredLegendName=="f"):
            return curvesToPlot
                            
        curvesToPlot.append((xIndexSelection,yIndexSelection,desiredLegendName))


#Creates a dictionary to hold information about the units used. A number key is associated with a tuple containing the
#unit name and scaling factor from phantom units.
def createUnitDictionary():
    #Phantom unit conversions.
    M_kg=1.99e30 #Mass in kg.
    M_g=1.99e33 #Mass in g.
    D_m=696.0e6 #Distance in m.
    D_cm=696.0e8 #Distance in cm.
    D_sr=1.0 #Distance in solar radii
    T_s=1593.6 #Time in s.
    
    timeS=(0,("time (s)",T_s))
    timeYr=(1,("time (years)",T_s/(86400.0*365.25)))
    distanceCm=(2,("distance (cm)",D_cm))
    distanceM=(3,("distance (m)",D_m))
    distanceSr=(4,("distance (solar radii)",D_sr))
    massG=(5,("mass (g)",M_g))
    massKg=(6,("mass (kg)",M_kg))
    velocityCm_s=(7,("velocity (cm/s)",D_cm/T_s))
    velocityM_s=(8,("velocity (m/s)",D_m/T_s))
    velocityKm_s=(9,("velocity (km/s)",(D_m/1000.0)/T_s))
    forceDyn=(10,("force (dyn)",(M_g*D_cm)/(T_s*T_s)))
    forceN=(11,("force (N)",(M_kg*D_m)/(T_s*T_s)))
    angularmomentumGcm2_s=(12,("angular momentum (g cm^2/s)",(M_g*D_cm*D_cm)/T_s))
    angularmomentumKgM2_s=(13,("angular momentum (kg m^2/s)",(M_kg*D_m*D_m)/T_s))
    torqueDynCm=(14,("torque (dyn cm)",(M_g*D_cm*D_cm)/(T_s*T_s)))
    torqueNm=(15,("torque (Nm)",(M_kg*D_m*D_m)/(T_s*T_s)))
    densityG_cm3=(16,("density (g/cm^3)",M_g/(D_cm*D_cm*D_cm)))
    densityKg_m3=(17,("density (kg/m^3)",M_kg/(D_m*D_m*D_m)))
    energyErg=(18,("energy (erg)",(M_g*D_cm*D_cm)/(T_s*T_s)))
    energyJ=(19,("energy (J)",(M_kg*D_m*D_m)/(T_s*T_s)))
    
    unitDictionary=dict([timeS,timeYr,distanceCm,distanceM,distanceSr,massG,massKg,velocityCm_s,velocityM_s,velocityKm_s,forceDyn,forceN,angularmomentumGcm2_s,angularmomentumKgM2_s,torqueDynCm,torqueNm,densityG_cm3,densityKg_m3,energyErg,energyJ])
    return unitDictionary


def getPlotUnits(unitDictionary):
    print("Select the units for the x and y axes of the plot or plots.")
    
    for currentUnit in unitDictionary.items():
        currentUnitNumber=currentUnit[0]
        currentUnitName=currentUnit[1][0]
        print(" "+str(currentUnitNumber)+", "+currentUnitName)
        
    
    allowedUnitSelections=[str(i) for i in range(len(unitDictionary))]
    xUnitIndex=int(processAllowedUserInputs(allowedUnitSelections))
    yUnitIndex=int(processAllowedUserInputs(allowedUnitSelections))
    
    return unitDictionary[xUnitIndex],unitDictionary[yUnitIndex]
        

#Plots all of the user selected x and y plots on top of one another.
def plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits,multipleFiles):
    if(len(curvesToPlot)==0):
        print("There is nothing to plot")
        return
    
    plotFigure=plt.figure()
    plotAxes=plotFigure.gca()
    
    
    #The unit conversion factors from phantom units.
    xScaleFactor=xUnits[1]
    yScaleFactor=yUnits[1]
    
    #The axes names as determined by the chosen units.
    xAxisName=xUnits[0]
    yAxisName=yUnits[0]
    plotAxes.set_xlabel(xAxisName)
    plotAxes.set_ylabel(yAxisName)
    
    plotAxes.ticklabel_format(style="sci",scilimits=(0,0))
    
    
    for currentCurveToPlot in curvesToPlot:
        currentXColumnKey=currentCurveToPlot[0]
        currentYColumnKey=currentCurveToPlot[1]
        currentLegendName=currentCurveToPlot[2]
        
        xData=columnData[currentXColumnKey]["values"]
        yData=columnData[currentYColumnKey]["values"]
        
        #New lists scaled for the correct units are created for the x and y axes; if done in place
        #it would cause problems with shared columns between plots.
        xDataScaled=[i*xScaleFactor for i in xData]
        yDataScaled=[i*yScaleFactor for i in yData]
            
        plotAxes.plot(xDataScaled,yDataScaled,label=currentLegendName)
     
    legend=plotAxes.legend(loc=(1.025,0))
    legend.set_in_layout(True) #This along with the next line is needed to prevent a wide enough legend from being cut off by the figure's edge.
    plotFigure.tight_layout()
    
    plt.show()



def main():
    fileNames,openedFiles=openFiles()

    if(len(openedFiles)==0):
        print("There are no files selected.")
    else:
        columnData=getColumnData(fileNames,openedFiles)
        unitDictionary=createUnitDictionary()

        while(True):
            curvesToPlot=getColumnPairsToPlot(fileNames,columnData)
            xUnits,yUnits=getPlotUnits(unitDictionary)
            plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits,len(fileNames)>1)
    
            print("Do you want to create another plot with the file/s? Enter yes or no.")
            if(processAllowedUserInputs(["yes","no"])=="no"):
                break #The user has chosen not to create any more plots with the file/s.
                

if(__name__=="__main__"):
    main()
    

    