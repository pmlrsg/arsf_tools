#!/usr/bin/env python
#-*- coding:utf-8 -*-

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

###########################################################################
#This is the main interface python library for the Las1.3Reader c++ library
# Use it for reading / plotting LAS 1.3 data
###########################################################################

import sys
import pylab
import las13reader
from matplotlib.backends.backend_pdf import PdfPages

#wrapper class for the c++ wrapper
class las13():
    """
    Class to wrap the las13reader class to be more user friendly
    """
    def __init__(self,filename,quiet=True):
        """
        Constructor: takes a LAS 1.3 file as input
        """
        if isinstance(filename,str):
            self.reader=las13reader.Las1_3_handler(filename)
            self.reader.SetQuiet(quiet)
        else:
            raise Exception("Expected string argument for filename.")

    def points_in_bounds(self,bounds):
        """
        Function that searches the LAS file and returns all points within the given rectangular bounds.
        Inputs:
           bounds - a list of 4 floating point values describing north, south, west and east bounds.

        Returns:
           An object of type las13reader.PulseManager.
        """
        if not isinstance(bounds,list):
            raise Exception("Expected list argument for bounds (of length 4: north,south,west,east).")
        if len(bounds)!=4:
            raise Exception("Expected bounds list of length 4: north,south,west,east.")

        pmanager=self.reader.GetPointsInBounds(bounds[0],bounds[1],bounds[2],bounds[3])
        return pmanager

    def points_with_classification(self,classification):
        """
        Function that searches the LAS file and returns all points with the given classification value.
        Inputs:
           classification - an integer value of the classification to search for

        Returns:
           An object of type las13reader.PulseManager.
        """
        if not isinstance(classification,int):
            raise Exception("Expected int argument for classification.")

        pmanager=self.reader.GetPointsWithClassification(classification)
        return pmanager

    def read_like_book(self,npoints=1,reset=False):
        """
        Function that searches the LAS file and returns points in sequence up to npoints.
        Inputs:
           npoints - an integer value for the maximum number of points to read
           reset - a boolean that when True resets the reader back to the start of the file

        Returns:
           An object of type las13reader.PulseManager.
        """
        if not isinstance(npoints,int):
            raise Exception("Expected int argument for npoints.")
        if not isinstance(reset,bool):
            raise Exception("Expected bool argument for reset.")

        pmanager=self.reader.ReadLikeBook(npoints,reset)
        return pmanager

    def tidy(self):
        """
        Function to destroy and free up memory used in any current pulse managers
        """
        self.reader.DeletePulseManagers()

    ###############################################################################
    # Static methods below here - functions do not depend on an instance of las13
    ###############################################################################
    #function to return the waveform x,y,z and intensity values from a given pulse
    @staticmethod
    def waveform(pulse):
        """
        Function to return the waveform of intensity values from a given pulse object
        Input:
           pulse - a las13reader.Pulse object (such that pulsemanagers contain)

        Returns:
           The waveform as a dictionary with keys 'x','y','z', and 'intensity'.
        """
        if not isinstance(pulse,las13reader.Pulse):
            print "las13.waveform expects a Pulse object to be passed, not: %s"%type(pulse)
            return None
        #number of samples
        nsamples=pulse.nsamples()
        #return a dict of lists
        waveform={'x':[],'y':[],'z':[],'intensity':[]}
        for s in range(0,nsamples):
            samplePos=list(pulse.sampleXYZ(s))
            waveform['x'].append(samplePos[0])
            waveform['y'].append(samplePos[1])
            waveform['z'].append(samplePos[2])
            waveform['intensity'].append(pulse.sampleintensity(s))

        return waveform

    @staticmethod
    def discrete(pulse):
        """
        Function to return the discrete point information from the given pulse
        """
        discrete=[]
        for r in range(0,pulse.nreturns()):
            discrete.append(discretepoint(pulse,r))
        return discrete


    #Function to return some (requested) info about the given pulse
    @staticmethod
    def get_pulse_info(pulse,keyword):
        """
        Function to extract the requested information from the given pulse object. This
           is really just a helper function to convert vectors into lists.
        Inputs:
           pulse - the pulse object
           keyword - key to describe information requested

        Returns:
           the requested data
        """
        keywords=['time','nreturns','nsamples','origin','offset','scanangle','classification','returnlocs','disint']

        if keyword == 'time':
            return pulse.time()
        elif keyword == 'nreturns':
            return pulse.nreturns()
        elif keyword == 'nsamples':
            return pulse.nsamples()
        elif keyword == 'origin':
            return list(pulse.originXYZ())
        elif keyword == 'offset':
            return list(pulse.offsetXYZ())
        elif keyword == 'scanangle':
            return pulse.scanangle()
        elif keyword == 'classification':
            return list(pulse.classification())
        elif keyword == 'returnlocs':
            return list(pulse.returnpointlocation())
        elif keyword == 'disint':
            return list(pulse.discreteintensities())
        else:
            print "Keyword should be one of: ",keywords
            raise Exception("Unrecognised keyword in get_pulse_info: %s."%(keyword))

    #Function to plot the pulse
    @staticmethod
    def quick_plot_pulse(pulse,title=None,filename=None):
        """
        Function to produce a plot of the pulse waveform data
        Inputs:
           pulse - the pulse object
           title - a title to give the plot
           filename - if given the plot is saved to the filename, else displayed on screen
        """
        waveform=las13.waveform(pulse)
        pylab.plot(waveform['intensity'],'b-',label='Waveform')
        pylab.xlabel('Sample number')
        pylab.ylabel('Intensity')
        if title:
            pylab.title(title)
        pylab.ylim([0,pylab.ylim()[1]+5])
        pylab.legend()
        if filename:
            pylab.savefig(filename)
        else:
            pylab.show()

    @staticmethod
    def plot_all_pulses(pulsemanager,filename):
        """
        Function to plot every pulse within a pulsemanager and save to a PDF file
        Inputs:
           pulsemanager - the pulsemanager object to plot data from
           filename - the PDF filename to save the plots to
        """
        fileobj=PdfPages(filename)
        for p in range(pulsemanager.getNumOfPulses()):
            pulse=pulsemanager[p]
            waveform=las13.waveform(pulse)
            pylab.plot(waveform['intensity'],'b-',label='Waveform')
            pylab.plot( [x / pulse.sampletime() for x in las13.get_pulse_info(pulse,'returnlocs')],las13.get_pulse_info(pulse,'disint'),'ro',label='Discrete')
            pylab.xlabel('Sample number')
            pylab.ylabel('Intensity')
            pylab.title('Pulse with time: %f'%pulse.time())
            pylab.ylim([0,pylab.ylim()[1]+5])
            pylab.legend()
            fileobj.savefig()
            pylab.clf()
        fileobj.close()


class dpoint():
    """
    Simple helper class to describe a points position in X,Y,Z
    """
    def __init__(self,dposition):
        self.X=dposition[0]
        self.Y=dposition[1]
        self.Z=dposition[2]

class discretepoint():
    """
    Class to hold information on discrete points in a user friendly interface
    """
    def __init__(self,pulse,item):
        if not isinstance(pulse,las13reader.Pulse):
            raise Exception("Parameter 'pulse' should be of type las13reader.Pulse in discretepoint object")

        if not isinstance(item,int):
            raise Exception("Parameter 'item' should be of type integer in discretepoint object")

        #get the number of returns
        self.returns=pulse.nreturns()
        if item >= self.returns:
            raise Exception("Cannot create a discretepoint for return %d when only %d returns for given pulse"%(item,self.returns))

        #get all the discrete points
        points=list(pulse.discretepoints())
        #now convert and store as 'dpoint' object
        self.position=dpoint(points[item])
        #intensity
        self.intensity=list(pulse.discreteintensities())[item]
        #classification
        self.classification=list(pulse.classification())[item]
        #return number
        self.returnnumber=item
