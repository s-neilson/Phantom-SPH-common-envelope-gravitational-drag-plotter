import matplotlib
import matplotlib.pyplot as plt


#Creates the figure with plot controls and the functions that run when the controls are used.
def createControls(plotFigure,controlVariables,xUnits,yUnits):
    plotAxes=plotFigure.gca()
    xAxisName,xAxisUnit=xUnits[0:2]
    yAxisName,yAxisUnit=yUnits[0:2]
    currentLines=plotAxes.get_lines()

    #The functions that run when the controls are used as created below.
    def createNewCombinedLegend(): #Creates a non split legend.
        newCombinedLegend=plotAxes.legend(ncol=controlVariables[0],loc="best")
        newCombinedLegend.set_draggable(True)
                    
    def legendSplitToggle(event):
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
                    
        plotFigure.canvas.draw()
                
                        
    def increaseLegendColumnNumber(event):
        if(controlVariables[1]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables[0]=min(len(currentLines),controlVariables[0]+1)
            createNewCombinedLegend()
            plotFigure.canvas.draw()
                    
                
    def decreaseLegendColumnNumber(event):               
        if(controlVariables[1]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables[0]=max(1,controlVariables[0]-1)
            createNewCombinedLegend()
            plotFigure.canvas.draw()


    def toggleXAxisScientificNotation(event):
        controlVariables[2]= not controlVariables[2]
        plotAxes.ticklabel_format(axis="x",style="sci" if(controlVariables[2]) else "plain",scilimits=(0,0),useMathText=True)
        plotFigure.canvas.draw()

        if(controlVariables[2]):
            exponentText=plotAxes.get_xaxis().get_offset_text()
            plotAxes.set_xlabel(xAxisName+" ("+exponentText.get_text()+" "+xAxisUnit+")") #The exponent multiplier is placed in the axis label.
            plt.setp(exponentText,visible=False) #The original exponent multipler is hidden.
        else:
            plotAxes.set_xlabel(xUnits[0])

        plotFigure.canvas.draw()


    def toggleYAxisScientificNotation(event):
        controlVariables[3]= not controlVariables[3]
        plotAxes.ticklabel_format(axis="y",style="sci" if(controlVariables[3]) else "plain",scilimits=(0,0),useMathText=True)
        plotFigure.canvas.draw()

        if(controlVariables[3]):
            exponentText=plotAxes.get_yaxis().get_offset_text()
            plotAxes.set_ylabel(yAxisName+" ("+exponentText.get_text()+" "+yAxisUnit+")") #The exponent multiplier is placed in the axis label.
            plt.setp(exponentText,visible=False) #The original exponent multipler is hidden.
        else:
            plotAxes.set_ylabel(yUnits[0])

        plotFigure.canvas.draw()


    def toggleXAxisLabel(event):
        controlVariables[4]=not controlVariables[4]
        plt.setp(plotAxes.get_xaxis(),visible=controlVariables[4])
        plotFigure.canvas.draw()

    
    def toggleYAxisLabel(event):
        controlVariables[5]=not controlVariables[5]
        plt.setp(plotAxes.get_yaxis(),visible=controlVariables[5])
        plotFigure.canvas.draw()



                    
                            
    #The controls are created below.        
    controlFigure=plt.figure(figsize=(4,2))
    button1Axes=controlFigure.add_axes([0.3,0.75,0.4,0.15])
    button2Axes=controlFigure.add_axes([0.05,0.55,0.4,0.15])
    button3Axes=controlFigure.add_axes([0.55,0.55,0.4,0.15])
    button4Axes=controlFigure.add_axes([0.05,0.3,0.4,0.2])
    button5Axes=controlFigure.add_axes([0.55,0.3,0.4,0.2])
    button6Axes=controlFigure.add_axes([0.05,0.05,0.4,0.2])
    button7Axes=controlFigure.add_axes([0.55,0.05,0.4,0.2])
            
    button1=matplotlib.widgets.Button(ax=button1Axes,label="Toggle split legend")
    button2=matplotlib.widgets.Button(ax=button2Axes,label="Less legend columns")
    button3=matplotlib.widgets.Button(ax=button3Axes,label="More legend columns")
    button4=matplotlib.widgets.Button(ax=button4Axes,label="Toggle x axis\n scientific notation")
    button5=matplotlib.widgets.Button(ax=button5Axes,label="Toggle y axis\n scientific notation") 
    button6=matplotlib.widgets.Button(ax=button6Axes,label="Toggle x axis\n label visibility")
    button7=matplotlib.widgets.Button(ax=button7Axes,label="Toggle y axis\n label visibility") 
                        
    button1.on_clicked(legendSplitToggle)
    button2.on_clicked(decreaseLegendColumnNumber)
    button3.on_clicked(increaseLegendColumnNumber)
    button4.on_clicked(toggleXAxisScientificNotation)
    button5.on_clicked(toggleYAxisScientificNotation)
    button6.on_clicked(toggleXAxisLabel)
    button7.on_clicked(toggleYAxisLabel)
    return button1,button2,button3,button4,button5,button6,button7 #Returned so the button objects exist outside the scope of this function.