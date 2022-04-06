from collections import OrderedDict
import csv
import regex
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyfit
from numpy.polynomial.polynomial import polyval

from equation import getValidRpnExpression,getDataForRpnExpression
from controls import createControls


#Integrates yValues over xValues while adding a constant of integration to the output values.
def integrateValues(xValues,yValues,constantOfIntegration):
    if(len(xValues)!=len(yValues)):
        print("Lengths of lists do not match.")
        return None
       
    integralValues=[]
    currentIntegralValue=0.0
    
    for i in range(len(xValues)):
        currentXValue=xValues[i]
        currentYValue=yValues[i]
        previousXValue=xValues[max(0,i-1)] #The previous x and y values are equal to the current x and y values if the first
        previousYValue=yValues[max(0,i-1)] #element of the integral is being evaluated.
        
        currentIntegralValue+=(0.5*(currentXValue-previousXValue)*(currentYValue+previousYValue)) #Uses the area of a trapezium.
        integralValues.append(currentIntegralValue+constantOfIntegration)
        
    return integralValues
        


#Differentiates a list of values with respect to an equally sized other list of values. The derivative is sampled between
#two points averageRadius away from the central point.
def differentiateValues(xValues,yValues,averageRadius):
    if(len(xValues)!=len(yValues)):
        print("Lengths of lists do not match.")
        return None
    
    derivativeValues=[]
    
    for i in range(len(xValues)):
        #The min and max functions are used to ensure that indices outside of the list are not used.
        leftIndex=max(0,i-averageRadius)
        rightIndex=min(len(xValues)-1,i+averageRadius)
                        
        currentDerivativeValue=(yValues[rightIndex]-yValues[leftIndex])/(xValues[rightIndex]-xValues[leftIndex])
        derivativeValues.append(currentDerivativeValue)
        
    return derivativeValues





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

        currentColumnTitles=regex.findall("(?<=\[)([^\[]{1,})(?=\])",firstLine) #All substrings of the first line in the file with a length of at least 1 character between a [ and a ] and not containing a [ are found.    
        for j in currentColumnTitles: #Loops through all found column titles (column numbers and their names).
            columnNumber=regex.search("(?<=^)( *)([0-9]+)",j) #Gets a sequence of numbers following the start of the string and possibly some spaces.
            columnName=regex.search("(?<=^)( *[0-9]+ *)(.+)",j) #Gets the substring following the start of the string, possibly some spaces, a number and possibly some spaces.
            
            columnKey=columnNumber.group(2)
            columnDataIndex=int(columnKey)-1 #This number is shifted down by 1 because the column data list starts indices at zero while the numbers in the column titles start at 1.
            columnKeySuffix=chr(ord("a")+i) #The key associated with the column information has a letter after the number that changes depending
            columnKey+=columnKeySuffix #on what file the column belongs to. The letters start with a and advance through the Unicode characters.
            
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
        

        
def getColumnPairsToPlot(columnData):
    curvesToPlot=[] #Holds a list of tuples containing the keys of the x and y column pairs to be plotted along with the desired legend name.      
        
    
    while(True): #Loops every time a new column is created by the user.
        allowedColumnKeys=[i for i in columnData.keys()]    
        allowedSelections=[]
        allowedSelections.extend(allowedColumnKeys)
        allowedSelections.append("f") #The entry for choosing to stop selecting column pairs.
        allowedSelections.append("l") #The entry for creating a column based on a range between two values.
        allowedSelections.append("e") #The entry for RPN expression input.
        allowedSelections.append("i") #The entry for integration.
        allowedSelections.append("d") #The entry for differentiation.
        allowedSelections.append("p") #The entry for a polynomial fit.
    
        print("List of columns that can be plotted:")
        previousFileName=""    
        for currentKey,currentColumnData in columnData.items(): #Loops through all columns.
            currentFileName=currentColumnData["fileName"]
            currentColumnName=currentColumnData["columnName"]
            currentColumnLength=str(len(currentColumnData["values"]))
            
            if(currentFileName!=previousFileName): #The file name is displayed if the current column is associated with a different file than the previous column.
                print(" "+currentFileName)
                previousFileName=currentFileName
                
            print("  "+currentKey+", "+currentColumnName+", ("+currentColumnLength+" values)")
       
        
        def addNewColumn(newColumnData):
            newColumnCount=0
            for currentKey in columnData.keys():
                if(currentKey[-1]=="_"): #If the current column has a key that ends with the _ character then it is a user made column.
                    newColumnCount+=1
            
            print("Enter a name for the new column")
            newColumnName=input()
            
            newColumn={"fileName":"User created columns","columnName":newColumnName,"values":newColumnData}
            newColumnKey=str(newColumnCount+1)+"_" #Keys for user created columns use the "_" character as a suffix.
            columnData[newColumnKey]=newColumn
            
            
        def createLinearColumn():
            print("Enter number of elements for the column to have")
            elementCount=int(input())
            print("Enter starting element")
            startingElement=float(input())
            print("Enter ending element")
            endingElement=float(input())
            
            differenceBetweenElements=(endingElement-startingElement)/(float(elementCount)-1.0)
            newColumnValues=[startingElement+(float(i)*differenceBetweenElements) for i in range(0,elementCount)]
            addNewColumn(newColumnValues)
                        
        
        def createColumnFromEquation():
            expressionList,expressionVariables=getValidRpnExpression(allowedColumnKeys)
            newColumnData=getDataForRpnExpression(columnData,expressionList,expressionVariables)
            addNewColumn(newColumnData)
            
        def createColumnFromIntegration():
            print("Enter column key to be integrated")
            yKey=processAllowedUserInputs(allowedColumnKeys)
            print("Enter column key to integrate over")
            xKey=processAllowedUserInputs(allowedColumnKeys)
            print("Enter constant of integration")
            constantOfIntegration=float(input())
            
            integralValues=integrateValues(columnData[xKey]["values"],columnData[yKey]["values"],constantOfIntegration)
            if(integralValues is not None): #A new column will not be added if the lists chosen for integration have different lengths.
                addNewColumn(integralValues)
                        
            
        def createColumnFromDifferentiation():
            print("Enter column key to be differentiated")
            yKey=processAllowedUserInputs(allowedColumnKeys)
            print("Enter column key to differentiate by")
            xKey=processAllowedUserInputs(allowedColumnKeys)            
            print("Enter distance from central point to calculate finite difference on")
            differentiationRadius=int(input())
            
            derivativeValues=differentiateValues(columnData[xKey]["values"],columnData[yKey]["values"],differentiationRadius)
            if(derivativeValues is not None): #A new column will not be added if the lists chosen for differentiation have different lengths.
                addNewColumn(derivativeValues)
                
        
        #Creates a column from a polynomial fitted to two sets of columns.
        def createColumnFromPolynomialFit():
            print("Enter column key for x axis")
            xKey=processAllowedUserInputs(allowedColumnKeys)
            print("Enter column key for y axis")
            yKey=processAllowedUserInputs(allowedColumnKeys)
            print("Enter fit order")
            fitOrder=int(input())
            
            xData=columnData[xKey]["values"]
            yData=columnData[yKey]["values"]
            if(len(xData)==len(yData)): #If the x and y data point sets have the same length.
                fitCoefficients=polyfit(xData,yData,fitOrder,full=False)
                fittedValues=polyval(xData,fitCoefficients)
                print("Polynomial fit coefficients in order from the lowest to heighest are: "+str(fitCoefficients))
                addNewColumn(fittedValues)
                
                                         
    
        while(True): #Loops while the user is selecting columns to plot.
            print("Select the x index, y index and desired legend name corresponding to what you want to plot, separated by commas. Enter f in you are finished with selecting columns to plot.")
            print("")
            print("Other options are:")
            print("l for a linearly spaced column created between two values.")
            print("e for a column created from reverse polish notation expression.")
            print("i for a column that is the integral of a column with respect to another column.")
            print("d for a column that is the derivative of a column with respect to another column.")
            print("p for column created from a polynomial fit of two other columns.")
                        
            columnChoiceString=input()
            columnChoiceList=regex.findall("(?<=(^|,))([^,]*)(?=($|,))",columnChoiceString) #Splits the string up in order with commas as the separator.

            xIndexSelection=columnChoiceList[0][1]           
            if(xIndexSelection not in allowedSelections):
                print("An invalid choice was given for the x axis or option choice.")
                continue
        
            if(xIndexSelection=="f"):
                return curvesToPlot
            
            if(xIndexSelection=="l"):
                createLinearColumn()
                break
        
            if(xIndexSelection=="e"):
                createColumnFromEquation()
                break
            
            if(xIndexSelection=="i"):
                createColumnFromIntegration()
                break           
            
            if(xIndexSelection=="d"):
                createColumnFromDifferentiation()
                break
            
            if(xIndexSelection=="p"):
                createColumnFromPolynomialFit()
                break
            


            if(len(columnChoiceList)!=3):
                print("There needs to be three comma separated strings in the user input or a single valid option choice.")
                continue

            yIndexSelection=columnChoiceList[1][1]
            if(yIndexSelection not in allowedColumnKeys):
                print("An invalid choice was given for the y axis.")
                continue
                     
            desiredLegendName=columnChoiceList[2][1]
                               
            curvesToPlot.append((xIndexSelection,yIndexSelection,desiredLegendName))


#Creates a dictionary to hold information about the units used. A number key is associated with a tuple containing the
#axis name, unit name and scaling factor from phantom units.
def createUnitDictionary():
    #Phantom unit conversions.
    M_kg=1.99e30 #Mass in kg.
    M_g=1.99e33 #Mass in g.
    M_sm=1.0 #Mass in solar masses.
    D_m=696.0e6 #Distance in m.
    D_cm=696.0e8 #Distance in cm.
    D_sr=1.0 #Distance in solar radii
    T_s=1593.6 #Time in s.
    
    
    timeS=("time","s",T_s)
    timeYr=("time","years",T_s/(86400.0*365.25))
    distanceCm=("distance","cm",D_cm)
    distanceM=("distance","m",D_m)
    distanceSr=("distance","$R\odot$",D_sr)
    massG=("mass","g",M_g)
    massKg=("mass","kg",M_kg)
    massSm=("mass","$M\odot$",M_sm)
    velocityCm_s=("velocity","cm/s",D_cm/T_s)
    velocityM_s=("velocity","m/s",D_m/T_s)
    velocityKm_s=("velocity","km/s",(D_m/1000.0)/T_s)
    forceDyn=("force","dyn",(M_g*D_cm)/(T_s*T_s))
    forceN=("force","N",(M_kg*D_m)/(T_s*T_s))
    angularmomentumGcm2_s=("angular momentum","g cm^2/s",(M_g*D_cm*D_cm)/T_s)
    angularmomentumKgM2_s=("angular momentum","kg m^2/s",(M_kg*D_m*D_m)/T_s)
    torqueDynCm=("torque","dyn cm",(M_g*D_cm*D_cm)/(T_s*T_s))
    torqueNm=("torque","Nm",(M_kg*D_m*D_m)/(T_s*T_s))
    densityG_cm3=("density","g/cm^3",M_g/(D_cm*D_cm*D_cm))
    densityKg_m3=("density","kg/m^3",M_kg/(D_m*D_m*D_m))
    energyErg=("energy","erg",(M_g*D_cm*D_cm)/(T_s*T_s))
    energyJ=("energy","J",(M_kg*D_m*D_m)/(T_s*T_s))
    phantomUnit1CustomLabel=("Custom phantom unit 1","",1.0)
    phantomUnit2CustomLabel=("Custom phantom unit 2","",1.0)
    
    unitList=[timeS,timeYr,
              distanceCm,distanceM,distanceSr,
              massG,massKg,massSm,
              velocityCm_s,velocityM_s,velocityKm_s,
              forceDyn,forceN,
              angularmomentumGcm2_s,angularmomentumKgM2_s,
              torqueDynCm,torqueNm,
              densityG_cm3,densityKg_m3,
              energyErg,energyJ,
              phantomUnit1CustomLabel,phantomUnit2CustomLabel]
    
    unitListWithKeys=[(key,value) for key,value in enumerate(unitList)] #Uses sequential numbers as keys for the units in the order they were added to the list.   
    unitDictionary=dict(unitListWithKeys)
    return unitDictionary


def getPlotUnits(unitDictionary):
    print("Select the units for the x and y axes of the plot or plots.")
    
    for currentUnit in unitDictionary.items():
        currentUnitNumber=currentUnit[0]
        currentUnitName=currentUnit[1][0]+" ("+currentUnit[1][1]+")"
        print(" "+str(currentUnitNumber)+", "+currentUnitName)
        
    
    allowedUnitSelections=[str(i) for i in range(len(unitDictionary))]
    xUnitIndex=int(processAllowedUserInputs(allowedUnitSelections))
    yUnitIndex=int(processAllowedUserInputs(allowedUnitSelections))
    
    
    numberOfUnits=len(unitDictionary)
    #Custom unit label selection is below. Assumes that the custom phantom units are the last two units.
    if((xUnitIndex==(numberOfUnits-2))or(yUnitIndex==(numberOfUnits-2))):
        print("Enter axis name for custom phantom unit 1")
        customAxisName=input()
        print("Enter unit name for custom phantom unit 1")
        customUnitName=input()
        unitDictionary[numberOfUnits-2]=(customAxisName,customUnitName,1.0)
        
    if((xUnitIndex==(numberOfUnits-1))or(yUnitIndex==(numberOfUnits-1))):
        print("Enter axis name for custom phantom unit 2")
        customAxisName=input()
        print("Enter unit name for custom phantom unit 1")
        customUnitName=input()
        unitDictionary[numberOfUnits-1]=(customAxisName,customUnitName,1.0)
 
    
    return unitDictionary[xUnitIndex],unitDictionary[yUnitIndex]
        

#Plots all of the user selected x and y plots on top of one another.
def plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits):
    if(len(curvesToPlot)==0):
        return None
    
    plotFigure=plt.figure()
    plotAxes=plotFigure.gca()
    
    #The unit conversion factors from phantom units.
    xScaleFactor=xUnits[2]
    yScaleFactor=yUnits[2]
    
    #The axes names as determined by the chosen units.
    xAxisName,xAxisUnit=xUnits[0:2]
    yAxisName,yAxisUnit=yUnits[0:2]
    plotAxes.set_xlabel(xAxisName+" ("+xAxisUnit+")")
    plotAxes.set_ylabel(yAxisName+" ("+yAxisUnit+")")
    
    plotAxes.ticklabel_format(style="sci",scilimits=(0,0),useMathText=True)
    plotAxes.grid(visible=False)
    

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

     
    legend=plotAxes.legend(loc="best")
    legend.set_draggable(True)
    plotFigure.tight_layout()
    
    return plotFigure



def main():
    fileNames,openedFiles=openFiles()

    columnData=getColumnData(fileNames,openedFiles)

    while(True):
        unitDictionary=createUnitDictionary()
        curvesToPlot=getColumnPairsToPlot(columnData)
        
        if(len(curvesToPlot)==0):
            print("There is nothing to plot.")
        else:
            xUnits,yUnits=getPlotUnits(unitDictionary)
            
            plotFigure=plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits)
            controlVariables={"fontSize":matplotlib.rcParams["font.size"],"legendColumnCount":1,"legendVisible":True,"legendSplit":False,"xAxisUseScientificNotation":True,"yAxisUseScientificNotation":True,"xAxisTextVisible":True,"yAxisTextVisible":True,"gridVisible":False}
            createdButtons=createControls(plotFigure,controlVariables,xUnits,yUnits)
  
            plt.show(block=True)
            
        print("Do you want to create another plot with the file/s? Enter yes or no.")
        if(processAllowedUserInputs(["yes","no"])=="no"):
            break #The user has chosen not to create any more plots with the file/s.
                

if(__name__=="__main__"):
    main()

    