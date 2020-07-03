from collections import OrderedDict
import csv
import re
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt



def rpnTokenIsOperator(token):
    return (token in ["+","-","*","/","^"])


def rpnTokenIsNumber(token):
    tokenNumber=0.0
    
    try:
        tokenNumber=float(token)
    except ValueError: #Casting the token to a number has failed.
        return False
    
    tokenNumber+=1.0 #To prevent a variable not being used error.
    return True


def rpnTokenIsVariable(token):
    return (not rpnTokenIsOperator(token)) and (not rpnTokenIsNumber(token))


#Turns an RPN expression into a list of tokens.
def rpnTurnIntoList(expressionString):
    outputList=[] #A list of the tokens in the expression.
    currentToken="" #Holds the current token that is being constructed.
    
    for i,currentCharacter in enumerate(expressionString):
        if(currentCharacter==" "): #The current token has ended, meaning that it is added to the output list.
            outputList.append(currentToken)
            currentToken="" #The current token is reset.
        else:
            currentToken+=currentCharacter #The current token is continued to be constructed.
            
        if((i+1)==len(expressionString)): #If the final character in the string has been reached.
            outputList.append(currentToken)
            
    return outputList


#Gets the variables to the filled in in an RPN expression.
def rpnGetVariables(expressionList,allowedVariableList):
    variableList=[] #An array of tuples that hold variable names and indices.
    
    for i,currentToken in enumerate(expressionList):
        if(rpnTokenIsVariable(currentToken)):           
            if((currentToken in allowedVariableList)==False):
                return [] #An empty list is returned if the variable name is not allowed.
            
            currentVariable=(currentToken,i)
            variableList.append(currentVariable)
            
    return variableList


#Checks if an RPN expression is valid.
def rpnCheckValidExpression(expressionList):
    rpnStackSize=0 #Only the stack size is needed, not the stack itself.
    
    for currentToken in expressionList:
        if(rpnTokenIsOperator(currentToken)): #If the current token is an operator
            rpnStackSize-=1 #Due to an operator removing two numbers from the stack and adding a result back into it.
        else: #The current token is a number that needs to be added to the stack.
            rpnStackSize+=1
            
        if(rpnStackSize<1):
            return False #An invalid expression has resulted in too many items being removed from the stack.
        
    return rpnStackSize==1 #The expression is valid if only one element (the result) is left in the stack.


def getValidRpnExpression(allowedVariableList):
    print("Type a valid reverse polish notation expression. Tokens must be separated by spaces. Data columns are referenced by using their key as a token. Allowed operators are +,-,*,/ and ^.")
    
    while(True):
        expressionString=input()
        expressionList=rpnTurnIntoList(expressionString)
        expressionVariables=rpnGetVariables(expressionList,allowedVariableList)
        
        if(len(expressionVariables)==0):
            print("That RPN expression is invalid either due to non recognised variable names or no variables.")
            continue
                
        if(rpnCheckValidExpression(expressionList)):
            return (expressionList,expressionVariables)
        else:
            print("That RPN expression is syntacically invalid.")
 

#Parses an RPN expression (in list form) and returns the result
def rpnParse(expressionList):
    rpnStack=[]
    
    for currentToken in expressionList:
        if(rpnTokenIsNumber(currentToken)):
            rpnStack.append(float(currentToken))
        elif(rpnTokenIsOperator(currentToken)):
            #The last two number on the stack are removed.
            rightNumber=rpnStack.pop()
            leftNumber=rpnStack.pop()
            
            currentResult=0.0 #Holds the result of the operation of the two removed numbers.
            if(currentToken=="+"):
                currentResult=leftNumber+rightNumber
            elif(currentToken=="-"):
                currentResult=leftNumber-rightNumber
            elif(currentToken=="*"):
                currentResult=leftNumber*rightNumber
            elif(currentToken=="/"):
                currentResult=leftNumber/rightNumber
            elif(currentToken=="^"):
                currentResult=leftNumber**rightNumber
            else:
                currentResult=0.0
                
            rpnStack.append(currentResult)
            

    return rpnStack[0] #The size of the stack at the end will be one element and this element is the answer to the expression.


#Creates a list of datapoints to be computed from an RPN expression containing references to columns.
def getDataForRpnExpression(columnData,expressionList,expressionVariables):
    expressionResult=[] #A list to hold all the computed datapoints.
    
    currentRow=0
    commonDatapointsExist=True
    while(commonDatapointsExist): #This loop goes through all rows common to the variables columns in the expression.
        
        #This loop replaces the variables in expressionList with values from the correct columns.
        for currentVariable in expressionVariables:
            currentVariableKey=currentVariable[0]
            currentColumnData=columnData[currentVariableKey]["values"]
                        
            currentDatapoint=currentColumnData[currentRow]
            currentVariableIndex=currentVariable[1] #The index of the element in expressionList to be replaced by the data corresponding to currentDatapoint
            expressionList[currentVariableIndex]=str(currentDatapoint) #The RPN parser expects all tokens to be strings.
            
            if((currentRow+1)==len(currentColumnData)):
                commonDatapointsExist=False #There is no further data in at least one of the columns, so further iterations of the while loop are stopped.
                
        currentComputedDatapoint=rpnParse(expressionList)
        expressionResult.append(currentComputedDatapoint) #The datapoint computed from the expression is added to the result list.
        currentRow+=1
        
    return expressionResult
        
                

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
        

        
def getColumnPairsToPlot(fileNames,columnData):
    curvesToPlot=[] #Holds a list of tuples containing the keys of the x and y column pairs to be plotted along with the desired legend name.
    
    allowedColumnIndices=[i for i in columnData.keys()]    
    allowedSelections=[]
    allowedSelections.extend(allowedColumnIndices)
    allowedSelections.append("f") #The entry for choosing to stop selecting column pairs.
    allowedSelections.append("e") #The entry for RPN expression input.
    
    
    print("List of columns that can be plotted:")
    previousFileName=""    
    for currentKey,currentColumnData in columnData.items(): #Loops through all columns.
            currentFileName=currentColumnData["fileName"]
            currentColumnName=currentColumnData["columnName"]
            
            if(currentFileName!=previousFileName): #The file name is displayed if the current column is associated with a different file than the previous column.
                print(" "+currentFileName)
                previousFileName=currentFileName
                
            print("  "+currentKey+", "+currentColumnName)
    
    
    while(True):
        print("Select the x index, y index and desired legend name corresponding to what you want to plot. Enter e if you want to input an expression. Enter f if you are finished with selecting columns to plot.")
    
                
        xIndexSelection=processAllowedUserInputs(allowedSelections)
        
        if(xIndexSelection=="f"):
            return curvesToPlot
        
        if(xIndexSelection=="e"):
            xIndexSelection=getValidRpnExpression(allowedColumnIndices)
                
        
        yIndexSelection=processAllowedUserInputs(allowedSelections)
        
        if(yIndexSelection=="f"):
            return curvesToPlot
        
        if(yIndexSelection=="e"):
            yIndexSelection=getValidRpnExpression(allowedColumnIndices)
            
        
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
    phantomUnit1CustomLabel=(20,("Custom phantom unit 1",1.0))
    phantomUnit2CustomLabel=(21,("Custom phantom unit 2",1.0))
    
    unitDictionary=dict([timeS,timeYr,distanceCm,distanceM,distanceSr,massG,massKg,velocityCm_s,velocityM_s,velocityKm_s,forceDyn,forceN,angularmomentumGcm2_s,angularmomentumKgM2_s,torqueDynCm,torqueNm,densityG_cm3,densityKg_m3,energyErg,energyJ,phantomUnit1CustomLabel,phantomUnit2CustomLabel])
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
    
    #Custom unit label selection is below.
    if((xUnitIndex==20)or(yUnitIndex==20)):
        print("Enter label for custom phantom unit 1")
        selectedLabel=input()
        unitDictionary[20]=(selectedLabel,1.0)
        
    if((xUnitIndex==21)or(yUnitIndex==21)):
        print("Enter label for custom phantom unit 2")
        selectedLabel=input()
        unitDictionary[21]=(selectedLabel,1.0)
 
    
    return unitDictionary[xUnitIndex],unitDictionary[yUnitIndex]
        

#Plots all of the user selected x and y plots on top of one another.
def plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits):
    if(len(curvesToPlot)==0):
        return None
    
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
        
        xData=[]
        yData=[]
        
        if(type(currentXColumnKey)==str):
            xData=columnData[currentXColumnKey]["values"]
        else: #It is an RPN expression
            xData=getDataForRpnExpression(columnData,currentXColumnKey[0],currentXColumnKey[1])
         
        if(type(currentYColumnKey)==str):
            yData=columnData[currentYColumnKey]["values"]
        else:
            yData=getDataForRpnExpression(columnData,currentYColumnKey[0],currentYColumnKey[1])
        
        #New lists scaled for the correct units are created for the x and y axes; if done in place
        #it would cause problems with shared columns between plots.
        xDataScaled=[i*xScaleFactor for i in xData]
        yDataScaled=[i*yScaleFactor for i in yData]
            
        plotAxes.plot(xDataScaled,yDataScaled,label=currentLegendName)

     
    legend=plotAxes.legend(loc="best")
    legend.set_draggable(True)
    plotFigure.tight_layout()
    
    return plotFigure

#Creates the figure with plot controls and the functions that run when the controls are used.
def createControls(plotFigure,controlVariables):
    plotAxes=plotFigure.gca()
    currentLines=plotAxes.get_lines()

    #The functions that run when the controls are used as created below.
    def createNewCombinedLegend(): #Creates a non split legend.
        newCombinedLegend=plotAxes.legend(ncol=controlVariables[0],loc="best")
        newCombinedLegend.set_draggable(True)
                    
    def legendSplitToggle(event):
        plt.sca(plotAxes)  
        controlVariables[1]=not controlVariables[1]
        
        if(controlVariables[1]):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            currentLegendXShift=0.0 #Used to prevent all the new legends from being on top of each other.
                        
            for currentLine in currentLines:
                newSplitLegend=plotAxes.legend(handles=[currentLine],loc=(0.25+currentLegendXShift,0.5))
                newSplitLegend.set_draggable(True)
                newSplitLegend.remove() #Done to prevent the legend being added twice to the figure.
                plotAxes.add_artist(a=newSplitLegend)
                currentLegendXShift+=0.05 #The next legend is shifted.
                            
        else: #The split legends are found and then removed.
            splitLegends=plotAxes.findobj(match=matplotlib.legend.Legend)
            for currentSplitLegend in splitLegends:
                currentSplitLegend.remove()
                createNewCombinedLegend()
                    
        plt.draw()
                
                        
    def increaseLegendColumnNumber(event):
        plt.sca(plotAxes)
                
        if(controlVariables[1]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables[0]=min(len(currentLines),controlVariables[0]+1)
            createNewCombinedLegend()
            plt.draw()
                    
                
    def decreaseLegendColumnNumber(event):
        plt.sca(plotAxes)
                
        if(controlVariables[1]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables[0]=max(1,controlVariables[0]-1)
            createNewCombinedLegend()
            plt.draw()
                    
                            
    #The controls are created below.        
    controlFigure=plt.figure(figsize=(4,2))
    button1Axes=controlFigure.add_axes([0.3,0.5,0.4,0.15])
    button2Axes=controlFigure.add_axes([0.05,0.3,0.4,0.15])
    button3Axes=controlFigure.add_axes([0.55,0.3,0.4,0.15])
            
    button1=matplotlib.widgets.Button(ax=button1Axes,label="Toggle split legend")
    button2=matplotlib.widgets.Button(ax=button2Axes,label="Less legend columns")
    button3=matplotlib.widgets.Button(ax=button3Axes,label="More legend columns")
                        
    button1.on_clicked(legendSplitToggle)
    button2.on_clicked(decreaseLegendColumnNumber)
    button3.on_clicked(increaseLegendColumnNumber)
    return button1,button2,button3 #Returned so the button objects exist outside the scope of this function.




def main():
    fileNames,openedFiles=openFiles()

    if(len(openedFiles)==0):
        print("There are no files selected.")
    else:
        columnData=getColumnData(fileNames,openedFiles)

        while(True):
            unitDictionary=createUnitDictionary()
            curvesToPlot=getColumnPairsToPlot(fileNames,columnData)
            xUnits,yUnits=getPlotUnits(unitDictionary)
            
            plotFigure=plotColumnPairs(columnData,curvesToPlot,xUnits,yUnits)
            if(plotFigure is not None): #If there is something to plot.
                controlVariables=[1,False] #Holds the number of columns in a non plit legend and whether the legend has been split.
                b1,b2,b3=createControls(plotFigure,controlVariables)
  
                plt.show(block=True)
            else:
                print("There is nothing to plot")
            
            print("Do you want to create another plot with the file/s? Enter yes or no.")
            if(processAllowedUserInputs(["yes","no"])=="no"):
                break #The user has chosen not to create any more plots with the file/s.
                

if(__name__=="__main__"):
    main()

    