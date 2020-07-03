# Phantom-SPH-common-envelope-gravitational-drag-plotter

Designed to plot the .ev file outputs of the gravitational drag section of the common envelope analyzer in Phantom SPH (https://phantomsph.bitbucket.io/). 

It has the following features:
*It allows the user to choose what column pairs of data they want to plot on a matplotlib plotting output. 
*Column pairs can be sourced from one file or many.
*Data to plot can be generated from reverse polish notation expressions involving existing column data.
*The user can choose what units the axes of the plot will be displayed in. These units assume that the original data is using the Phantom unit system (mass=solar mass, distance=solar radius, time=1593.6s).

It can also plot files containing data arranged in columns separated by a space followed possibly by whitespace and rows separated by new lines. The first line in the file must contain the names of the columns and the column number (starting from 1, not 0) inside "[]" type brackets in the following format: [ number   name] [number  name]  [    number  name]. The text inside the brackets needs to be 15 characters long, spaces inside the brackets can be used multiple times after one another, number must be written using numerals, the brackets must be seperated by at least one space followed possibly by whitespace and the number of column names with column numbers inside brackets must be equal to or less than the total number of columns of data. Data in the file also must be able to be converted to a float using the float() function in Python.


This program has been tested using Python 3.7.7
