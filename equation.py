import regex

#Operators with one argument.
def rpnTokenIs1Operator(token):
    return (token in ["h","abs"])

#Operators with two arguments.
def rpnTokenIs2Operator(token):
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
    return (not rpnTokenIs1Operator(token)) and (not rpnTokenIs2Operator(token)) and (not rpnTokenIsNumber(token))


#Turns an RPN expression into a list of tokens.
def rpnTurnIntoList(expressionString):     
    foundTokens=regex.findall("(?<=(^| ))([^ ]*)(?=($| ))",expressionString) #Finds all text separated by spaces.
    outputList=[i[1] for i in foundTokens] #Removes the spaces to the sides of the found tokens.
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
        if(rpnTokenIs2Operator(currentToken)): #If the current token is an operator
            rpnStackSize-=1 #Due to the operator removing two numbers from the stack and adding a result back into it.
        elif(not rpnTokenIs1Operator(currentToken)): #The current token is a number that needs to be added to the stack.
            rpnStackSize+=1
            
        if(rpnStackSize<1):
            return False #An invalid expression has resulted in too many items being removed from the stack.
        
    return rpnStackSize==1 #The expression is valid if only one element (the result) is left in the stack.


def getValidRpnExpression(allowedVariableList):
    print("Type a valid reverse polish notation expression. Tokens must be separated by spaces. Data columns are referenced by using their key as a token. Allowed operators are +,-,*,/,^,h (Heaviside step function) and abs (absolute value).")
    
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
        elif(rpnTokenIs1Operator(currentToken)):
            rightNumber=rpnStack.pop()
            
            currentResult=0.0 #Holds the result of the operation on the removed number.
            
            if(currentToken=="h"): #Heaviside step function.
                currentResult=0.0 if(rightNumber<0.0) else 1.0
                
            if(currentToken=="abs"): #Absolute value.
                currentResult=abs(rightNumber)
                
            rpnStack.append(currentResult)
            
        elif(rpnTokenIs2Operator(currentToken)):
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