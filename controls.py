import matplotlib
import matplotlib.pyplot as plt


#Creates the figure with plot controls and the functions that run when the controls are used.
def createControls(plotFigure,controlVariables,xUnits,yUnits):
    plotAxes=plotFigure.gca()
    xAxisName,xAxisUnit=xUnits[0:2]
    yAxisName,yAxisUnit=yUnits[0:2]
    currentLines=plotAxes.get_lines()

    #The functions that run when the controls are used as created below.
    def toggleLegendVisibility():
        controlVariables["legendVisibility"]=not controlVariables["legendVisibility"]
        plt.setp(plotAxes.get_legend(),visible=controlVariables["legendVisibility"])
        plotFigure.canvas.draw()


    def createNewCombinedLegend(): #Creates a non split legend.
        newCombinedLegend=plotAxes.legend(ncol=controlVariables["legendColumnCount"],loc="best")
        newCombinedLegend.set_draggable(True)
                    
    def legendSplitToggle(event):
        controlVariables["legendSplit"]=not controlVariables["legendSplit"]
        
        if(controlVariables["legendSplit"]):
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
        if(controlVariables["legendSplit"]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables["legendColumnCount"]=min(len(currentLines),controlVariables["legendColumnCount"]+1)
            createNewCombinedLegend()
            plotFigure.canvas.draw()
                    
                
    def decreaseLegendColumnNumber(event):               
        if(controlVariables["legendSplit"]==False):
            (plotAxes.get_legend()).remove() #The current legend is removed.
            controlVariables["legendColumnCount"]=max(1,controlVariables["legendColumnCount"]-1)
            createNewCombinedLegend()
            plotFigure.canvas.draw()


    def toggleXAxisScientificNotation(event):
        controlVariables["xAxisUseScientificNotation"]= not controlVariables["xAxisUseScientificNotation"]
        plotAxes.ticklabel_format(axis="x",style="sci" if(controlVariables["xAxisUseScientificNotation"]) else "plain",scilimits=(0,0),useMathText=True)
        plotFigure.canvas.draw()

        if(controlVariables["xAxisUseScientificNotation"]):
            exponentText=plotAxes.get_xaxis().get_offset_text()
            plotAxes.set_xlabel(xAxisName+" ("+exponentText.get_text()+" "+xAxisUnit+")") #The exponent multiplier is placed in the axis label.
            plt.setp(exponentText,visible=False) #The original exponent multipler is hidden.
        else:
            plotAxes.set_xlabel(xAxisName+" ("+xAxisUnit+")")

        plotFigure.canvas.draw()


    def toggleYAxisScientificNotation(event):
        controlVariables["yAxisUseScientificNotation"]= not controlVariables["yAxisUseScientificNotation"]
        plotAxes.ticklabel_format(axis="y",style="sci" if(controlVariables["yAxisUseScientificNotation"]) else "plain",scilimits=(0,0),useMathText=True)
        plotFigure.canvas.draw()

        if(controlVariables["yAxisUseScientificNotation"]):
            exponentText=plotAxes.get_yaxis().get_offset_text()
            plotAxes.set_ylabel(yAxisName+" ("+exponentText.get_text()+" "+yAxisUnit+")") #The exponent multiplier is placed in the axis label.
            plt.setp(exponentText,visible=False) #The original exponent multipler is hidden.
        else:
            plotAxes.set_ylabel(yAxisName+" ("+yAxisUnit+")")

        plotFigure.canvas.draw()


    def toggleXAxisText(event):
        controlVariables["xAxisTextVisible"]=not controlVariables["xAxisTextVisible"]
        plotAxes.tick_params(axis="x",labelbottom=controlVariables["xAxisTextVisible"])
        plt.setp(plotAxes.get_xaxis().get_label(),visible=controlVariables["xAxisTextVisible"])
        plotFigure.canvas.draw()

    
    def toggleYAxisText(event):
        controlVariables["yAxisTextVisible"]=not controlVariables["yAxisTextVisible"]
        plotAxes.tick_params(axis="y",labelleft=controlVariables["yAxisTextVisible"])
        plt.setp(plotAxes.get_yaxis().get_label(),visible=controlVariables["yAxisTextVisible"])
        plotFigure.canvas.draw()


    def toggleGridVisibility(event):
        controlVariables["gridVisible"]=not controlVariables["gridVisible"]
        plotAxes.grid(visible=controlVariables["gridVisible"],which="major",axis="both")
        plotFigure.canvas.draw()


    def updateFontSize(newFontSize): #Changes the font size of the tick labels, axis labels and legend/s.
        plotAxes.tick_params(axis="both",labelsize=newFontSize)
        plt.setp(plotAxes.get_xaxis().get_label(),fontsize=newFontSize)
        plt.setp(plotAxes.get_yaxis().get_label(),fontsize=newFontSize)
        allLegends=plotAxes.findobj(match=matplotlib.legend.Legend)
        for cl in allLegends:
            plt.setp(cl.get_texts(),fontsize=newFontSize)

    def decreaseFontSize(event):
        controlVariables["fontSize"]=max(1,controlVariables["fontSize"]-1)
        updateFontSize(controlVariables["fontSize"])
        plotFigure.canvas.draw()


    def increaseFontSize(event):
        controlVariables["fontSize"]=min(50,controlVariables["fontSize"]+1)
        updateFontSize(controlVariables["fontSize"])
        plotFigure.canvas.draw()
     


                    
                            
    #The controls are created below.        
    controlFigure=plt.figure(figsize=(4,4))
    button1Axes=controlFigure.add_axes([0.3,0.62,0.4,0.1])
    button2Axes=controlFigure.add_axes([0.05,0.5,0.4,0.1])
    button3Axes=controlFigure.add_axes([0.55,0.5,0.4,0.1])
    button4Axes=controlFigure.add_axes([0.05,0.38,0.4,0.1])
    button5Axes=controlFigure.add_axes([0.55,0.38,0.4,0.1])
    button6Axes=controlFigure.add_axes([0.05,0.26,0.4,0.1])
    button7Axes=controlFigure.add_axes([0.55,0.26,0.4,0.1])
    button8Axes=controlFigure.add_axes([0.3,0.14,0.4,0.1])
    button9Axes=controlFigure.add_axes([0.05,0.02,0.4,0.1])
    button10Axes=controlFigure.add_axes([0.55,0.02,0.4,0.1])
    
            
    button1=matplotlib.widgets.Button(ax=button1Axes,label="Toggle split legend")
    button2=matplotlib.widgets.Button(ax=button2Axes,label="Less legend columns")
    button3=matplotlib.widgets.Button(ax=button3Axes,label="More legend columns")
    button4=matplotlib.widgets.Button(ax=button4Axes,label="Toggle x axis\n scientific notation")
    button5=matplotlib.widgets.Button(ax=button5Axes,label="Toggle y axis\n scientific notation") 
    button6=matplotlib.widgets.Button(ax=button6Axes,label="Toggle x axis\n text visibility")
    button7=matplotlib.widgets.Button(ax=button7Axes,label="Toggle y axis\n text visibility") 
    button8=matplotlib.widgets.Button(ax=button8Axes,label="Toggle grid visibility")
    button9=matplotlib.widgets.Button(ax=button9Axes,label="Decrease font size")
    button10=matplotlib.widgets.Button(ax=button10Axes,label="Increase font size")
                        
    button1.on_clicked(legendSplitToggle)
    button2.on_clicked(decreaseLegendColumnNumber)
    button3.on_clicked(increaseLegendColumnNumber)
    button4.on_clicked(toggleXAxisScientificNotation)
    button5.on_clicked(toggleYAxisScientificNotation)
    button6.on_clicked(toggleXAxisText)
    button7.on_clicked(toggleYAxisText)
    button8.on_clicked(toggleGridVisibility)
    button9.on_clicked(decreaseFontSize)
    button10.on_clicked(increaseFontSize)
    return button1,button2,button3,button4,button5,button6,button7,button8,button9,button10 #Returned so the button objects exist outside the scope of this function.