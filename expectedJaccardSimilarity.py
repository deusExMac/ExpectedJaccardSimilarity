'''

 Calculates empirically the expected value of the Jaccard similarity for
 exercise 3.1.3 (page 86) found in [1]. The exact expected value is given by formula in [2].

 It does this by repeatedly selecting randomly subsets S and T from the same
 universal set (U) using a uniform distribution and calculating their Jaccard similarity.
 The average of Jaccard similarities is calcualted and plotted. Uses animation
 capabilities of matplotlib.

 A number of settings are supported to further experiment with/check/debug the script. 
 
 This was based on an initial idea by Ioannis Refanidis (https://www.uom.gr/en/yrefanid)
 who did a first implementation for confirming the theoretically proven value.
 This gave me the idea to do a Python implementation in order to also experiment with
 the animation capabilities of matplotlib.


 References:
   1) Leskovec, J., Rajaraman, A., and Ullman, J. D.: Mining of Massive
      Datasets, Cambridge University Press, 2014. Available http://mmds.org

   2) File "Exercise 3.1.3 Solution".pdf



 v0.3/mmt/27092025 -- tzagara@upatras.gr

'''


import sys
import random
import os.path
from pathlib import Path
import time

import math
import numpy as np

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import jaccard_score
from matplotlib import pyplot as plt
import matplotlib.transforms as transforms
from matplotlib import animation
from statistics import mean
import datetime


import clrprint
import csv

import collections
import configargparse

import psutil






# Default  parameters
# If no other argument is provided, script will be executed
# with these default settings.

# The reference jaccard similarity
# NOTE: -1 means use as reference the exact theoretically calculated
#       expected value of the Jaccard similarity   
#DEFAULT_JACCARD_SIMILARITY_TARGET = 0.15551227322305261630785
DEFAULT_JACCARD_SIMILARITY_TARGET = -1

# How many random integers to generate
DEFAULT_UNIVERSAL_SET_SIZE = 100

# DEFAULT maximum integer value (range of values to choose DEFAULT_UNIVERSAL_SET_SIZE integers)
# Universal set will have integers in the range [0, MAX_INT-1].
#
# Note: Must me equal or larger than DEFAULT_UNIVERSAL_SET_SIZE. Otherwise, error is generated.
DEFAULT_MAX_INT = 100

# How many samples to generate and calculate Jaccard
# distances.
DEFAULT_N_SAMPLES = 100

# Sizes if S abd T sets
DEFAULT_S_SIZE = 20
DEFAULT_T_SIZE = 20


# If an epsilon is chosen, this specifies how many times
# the difference needs to fall below epsilon to terminate
# the process
DEFAULT_DELTA_STREAK = 3



class JaccardSimilarityPlot(object):
    
    def __init__(self, cfg={}):
        
        # Make sure to have a configuration
        if cfg is None:
           self.configuration = {}
        else:   
           self.configuration = cfg

        # Returns the univeral set (out of which the two random sets will be drawn) as a list   
        self.universalSet = random.sample(range(1, self.configuration.get('maxvalue', DEFAULT_MAX_INT)+1),
                                          self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE))

        if self.configuration.get('debug', False):
           print('[DEBUG] U=', self.universalSet)
           
        self.nPairs = 0
        # Storing pair number
        self.x = []
        # Storing jaccard similarities of pairs
        self.y = []
        # Storing some more info only for debugging purposes including generated sets S and T.
        self.yMeta = []

        self.maxJaccard = -1
        self.minJaccard = 100
        self.currentAverageJaccard = -1
        self.deltaStreak = 0

        # Storing distribution of generated numbers. Will happen only
        # when uniformitycheck is set.
        self.itemFrequency = {}

        self.startTime = -1
        self.stopTime = -1



       
    # TODO: complete me
    def shouldTerminate(self):
        '''
           Checks if script should terminate, based on the settings
           rovided.
        '''
        if self.configuration.get('epsilon', -1) > 0:
            
           if self.configuration.get('debug', False): 
                 clrprint.clrprint(f'[DEBUG] Current avg:{self.currentAverageJaccard} target:{self.configuration.get("targetexpectedjaccardsimilarity", DEFAULT_JACCARD_SIMILARITY_TARGET)} ε:{self.configuration.get("epsilon", 0.0)}', clr='yellow')


           if not np.isclose( [self.currentAverageJaccard], [self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET)], atol=self.configuration.get('epsilon', 0.0)):
              self.deltaStreak = 0 # reset
           else:
              self.deltaStreak += 1
              if self.deltaStreak >= self.configuration.get('deltastreak', DEFAULT_DELTA_STREAK):
                   print(f'\n\n[{getCurrentDateTime()}] [n={self.nPairs}, avg={self.currentAverageJaccard}] Reached below ε {self.configuration.get("epsilon", 0.0)} more than {self.configuration.get("deltastreak", DEFAULT_DELTA_STREAK)} times. Terminating.')
                   return(True)

                   
                
        elif self.configuration.get('nsamples', DEFAULT_N_SAMPLES)  > 0:
             if self.nPairs >= self.configuration.get('nsamples', DEFAULT_N_SAMPLES):
                return(True)
             
        return(False)      



    def delay(self, secs=5):
        for i in range(secs):
            clrprint.clrprint(secs-i, ' ', clr='red', end='')
            time.sleep(1)

        print('')
        return     



    def terminate(self):
        '''
           Terminates the script. Saves calculated similarities to files if so specified by the configuration.
           Terminates the script in the way the configuration specifies.
        '''

        self.stopTime = time.time()
        
        if self.configuration.get('savesimilarities', False):
           sFile = self.configuration.get('outputcsvfile', 'jaccardSimilarities') +  str(self.configuration.get('ssetsize', DEFAULT_S_SIZE)) + 'x' + str(self.configuration.get('tsetsize', DEFAULT_T_SIZE)) + 'x' + str(self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE)) + '.csv' 
           print(f'[{getCurrentDateTime()}] Saving to file {sFile}...', end='')  
           self.saveAsCSV(fname=sFile)
           print('done.')
           
        if not self.configuration.get('autoterminate', True):
           wait = input(f"[{getCurrentDateTime()}] Finished gracefully.\n\tn:{self.nPairs}\n\tAverage similarity:{self.currentAverageJaccard}\n\tExpected similarity:[{self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET)}\n\tDelta:{abs(self.currentAverageJaccard - self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET))}\n\tε:{self.configuration.get('epsilon', -1)}\n\telapsed:{'{:.3f}'.format(self.stopTime-self.startTime)}s\nPress enter to terminate...")
           print(f'[{getCurrentDateTime()}] ByeBye') 
        else:   
             print(f'[{getCurrentDateTime()}] Finished gracefully.\n\tn:{self.nPairs}\n\tAverage similarity:{self.currentAverageJaccard}\n\tExpected similarity:{self.configuration.get("targetexpectedjaccardsimilarity", DEFAULT_JACCARD_SIMILARITY_TARGET)}\n\tDelta:{abs(self.currentAverageJaccard - self.configuration.get("targetexpectedjaccardsimilarity", DEFAULT_JACCARD_SIMILARITY_TARGET))}\n\tε:{self.configuration.get("epsilon", -1)}\n\telapsed:{"{:.3f}".format(self.stopTime-self.startTime)}s') 
             print(f'[{getCurrentDateTime()}] Will terminate in ', end='')
             self.delay()     
             print(f'[{getCurrentDateTime()}] ByeBye')
             plt.close()

 
        if self.configuration.get('uniformitycheck', False):

           # Do some visual checks only to see if data used follows a uniform distribution.
           #
           # NOTE: A Kolmogorov-Smirnov test could be done which in Python is supported using the kstat function
           # from scipy.
           # However, executing the next two lines:
           #
           # from scipy import stats
           # res = stats.kstest(values, 'randint', args=(min(self.universalSet), max(self.universalSet)-min(self.universalSet)))
           #
           # will give a p-value < 0.01 which means that the null hypothesis that the sampled data is from a uniform distribution
           # is rejected. Same results are generated when uniform is used instead of randint. This is strange and something
           # is definitely missing or not properly done.
           # 
           # TODO: Look into Kolmogorov-Smirnov test and kstest in greater detail.  
           
           if self.configuration.get('debug', False):
              clrprint.clrprint('Counts:', collections.OrderedDict(sorted(self.itemFrequency.items())), clr='yellow')
           
           # Calculate cummulative distribution function based on actual counts seen

           # Transform  counts of sampled integers into probabilities 
           s = sum(list(self.itemFrequency.values()))
           orderedKeys = {key: (self.itemFrequency[key] / s) for key in self.itemFrequency.keys()}
           orderedKeys = collections.OrderedDict(sorted(orderedKeys.items()))
           if self.configuration.get('debug', False):
              clrprint.clrprint('Probabilities:', orderedKeys, clr='maroon')

           # ... and into cummulative probabilities in order to generate
           # the CDF of the actual counts.
           cumsum = 0
           for k, v in orderedKeys.items():
               cumsum += v
               orderedKeys[k] = cumsum
               
           if self.configuration.get('debug', False):
              clrprint.clrprint('Cumulative probabilities:', orderedKeys, clr='green')

           
           # Create two vertically stacked plots:
           # One wih a bar chart of the actual counts and the expected mean value and another one
           # with two CDFs: one cdf of the actual counts and one  cdf of the theoretical uniform distribution.
           
           fig, (ax1, ax2) = plt.subplots(2)

           ################################################################################################## 
           # 1st evidence: Barchart of counts with expected and average values of counts
           ##################################################################################################
           barChart = ax1.bar(self.itemFrequency.keys(), self.itemFrequency.values())
           ax1.tick_params(labelrotation=45)
           ax1.bar_label(barChart, label_type='edge', color='blue', fontsize=6)
           ax1.set_title("Counts", size=10)
           ax1.tick_params(axis='both', which='major', labelsize=8)
           
           # Display also expected (mean) value of counts
           ax1.axhline(y=self.nPairs*self.propabilityInSorT(), color='r', linestyle='-', linewidth=1.2)
           trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
           ax1.text(0, self.nPairs*self.propabilityInSorT(), "expected\n{:.2f}".format(self.nPairs*self.propabilityInSorT()), color="red", transform=trans, ha="right", va="center")

           # and the actual average value of counts
           ax1.axhline(y=mean(self.itemFrequency.values()), color='green', linestyle='-.', linewidth=1.2)



           ################################################################################################## 
           # 2nd evidence: Actual CDF vs Uniform CDF 
           ##################################################################################################
           # Visual indication to see if samples were selected uniformly.
           # 
           # CDF of actual and uniform distribution are displayed: these should match in order to verify that
           # the sample was drawn from a uniform distribution and that no sampling was not problematic.
           #values = orderedKeys.values()

           # CDF of actual distribution
           ax2.plot(orderedKeys.keys(), orderedKeys.values(), 'x', color='blue')
           
           # CDF of uniform distribution
           actualRange = range(1, max(self.universalSet)+1)
           expected = [i*(1/self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE)) for i in orderedKeys.keys()]
           ax2.plot(orderedKeys.keys(), expected, '.', color='red')
           ax2.legend(['CDF actual counts', 'CDF uniform'], loc="upper right")
           ax2.set_title("CDF: actual vs theoretical", size=10)
           ax2.tick_params(axis='both', which='major', labelsize=8)
           plt.show()
           

        self.logAverage()   
        sys.exit(0)     
        


    def logAverage(self, fn='averages.csv'):
        fileExists = os.path.isfile(fn)
        headers = ['timeStamp', 'U', 'S', 'T', 'n', 'e', 'avg', 'expected', 'delta', 'elapsed']
        logEntry = {'timeStamp':getCurrentDateTime(),
               'U':self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE),
               'S':self.configuration.get('ssetsize', DEFAULT_S_SIZE),
               'T':self.configuration.get('tsetsize', DEFAULT_T_SIZE),
               'n':self.nPairs,
               'e':self.configuration.get('epsilon', -1),
               'avg':self.currentAverageJaccard,
               'expected':self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET),
               'delta':abs(self.currentAverageJaccard - self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET)),
               'elapsed': "{:.3f}".format(self.stopTime - self.startTime)}

        with open (fn, 'a') as csvfile:
             writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
             if not fileExists:
                 writer.writeheader()  # file doesn't exist yet, write a header
                 
             writer.writerow(logEntry)


             

    def saveAsCSV(self, fname='jaccardSimilarites', sep=','):
        '''
           Saves the similarities along with a timestamp and any optional fields
           (sset and tset) in a file. 
        '''

        
        oFile = Path(fname)
        oFile.parent.mkdir(exist_ok=True, parents=True)

        fileExists = os.path.isfile(fname)
        headers = ['timeStamp']
        with open (fname, 'a') as csvfile:
             if ['sset'] in self.configuration.get('fields_list', []):
                headers.append('sset')
             if ['tset'] in self.configuration.get('fields_list', []):
                headers.append('tset')
                
             headers.append('jaccardSimilarity')
             
             writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)

             if not fileExists:
                 writer.writeheader()  # file doesn't exist yet, write a header

             for sim in self.yMeta:
                 writer.writerow(sim)


    def getScriptMemory(self):
        process = psutil.Process()
        return(process.memory_info().rss)
    


    #######################################################################################################################
    # Sampling and Jaccard related
    #######################################################################################################################

    @staticmethod
    def theoreticalExpectedValue(u=100, s=20, t=40):
        '''
           Calculates the theoretical expected value for the sizes of sets U, S and T based on the derived
           formula.
        '''
        n=u
        m1=min(s, t)
        m2=max(s, t)
        s=0
        for i in range(0, m1+1):
            s += (i/(m1+m2-i)) * (math.comb(n, i)*math.comb(n-i, m1-i)*math.comb(n-m1, m2-i)/(math.comb(n, m1)*math.comb(n, m2))) 

        return(s)


        
    def propabilityInSorT(self):
        return( (self.configuration.get('ssetsize', DEFAULT_S_SIZE)/self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE)) +
                (self.configuration.get('tsetsize', DEFAULT_T_SIZE)/self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE)) )



    
    # TODO: Complete this
    def calculateItemFrequency(self, randomItems):
        for itm in randomItems:
            if itm not in self.itemFrequency:
               self.itemFrequency[itm] = 1
            else:
               self.itemFrequency[itm] += 1 




    # Returns sets
    def getSandTSetsSHUFFLE(self, sizeS=DEFAULT_S_SIZE, sizeT=DEFAULT_T_SIZE):
        '''
           Gets and returns random sets S and T based on shuffling the
           universal list.
        '''   
        # NOTE: random parameter in shuffle is deprecated. 
        
        # Shuffles universal set.
        # Shuffling does a Fisher–Yates shuffle where each permutation is
        # equally likely. It's an unbiased permutator.
        # For more info see: https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
        
        S = list(self.universalSet)
        random.shuffle(S)
    
        T = list(self.universalSet)
        random.shuffle(T)

        if self.configuration.get('debug', False):
           print('\n[DEBUG] (Shuffle)\n\tS=', set(S[:sizeS]), '\n\tT=', set(T[:sizeT]), sep='')
           

        
        if self.configuration.get('uniformitycheck', False): 
           self.calculateItemFrequency(S[:sizeS])
           self.calculateItemFrequency(T[:sizeT])
           
        # Get first S_SIZE and T_SIZE elements from shuffled universal sets
        return(set(S[:sizeS]), set(T[:sizeT]))





    # Uses random.sample(). Returns sets
    def getSandTSetsRANDOMSAMPLE(self, sizeS=DEFAULT_S_SIZE, sizeT=DEFAULT_T_SIZE):
        '''
           Gets and returns random sets S and T based on sampling the
           universal list.
        '''
        S = random.sample(self.universalSet, sizeS)
        T = random.sample(self.universalSet, sizeT)
        if self.configuration.get('debug', False):
           print('\n[DEBUG] (Random sample)\n\tS=', set(S), '\n\tT=', set(T), sep='')
        
        if self.configuration.get('uniformitycheck', False): 
           self.calculateItemFrequency(S)
           self.calculateItemFrequency(T)
           
        return(set(S), set(T))





    def jaccardSimilarity(self, s1, s2):
        '''
           Calculates Jaccard similarity based on definition of Jaccard.
        '''  
        return( len(s1.intersection(s2)) / len(s1.union(s2)) )



        
    def sklearnJaccard(self, s1, s2):
        '''
           Calculates Jaccard similarity by one-hot encoding the sets
           and using the Jaccard similarity function from sklearn.
        '''
        mlb = MultiLabelBinarizer()
        # One hot encoding.
        mlf=mlb.fit_transform([s1, s2])
        sList=mlf[0,:].tolist()
        tList=mlf[1,:].tolist()
        return(jaccard_score(sList, tList, average='binary'))




    #######################################################################################################################
    # Drawing related
    #######################################################################################################################

    def doPlot(self, jaccardSimilarity):
        '''
           Takes as input the returned value from update() -a Jaccard similarity for a new pair of sets S and T
           and animates it on plot.
           Updates also the status labels and checks if termination criteria are met.
        '''

        
        if self.configuration.get('debug', False): 
            print(f'[DEBUG] >>> [n={self.nPairs}] Curr:{jaccardSimilarity}. Avg: {self.currentAverageJaccard}')
            
        
        ws = self.configuration.get('windowsize', 50)
        if ws <= 0:
           ws = 0

        
        
        
        # Clear plot
        plt.clf()

        
        plt.title('Expected and average value of Jaccard similarity')

        # Plot last calculated Jaccard values as defined by the window size
        plt.plot(self.x[-ws:], self.y[-ws:], color='g', marker='o', linestyle='dotted', markersize=4,  label='Jaccard similarity of random sample')

        # Place some calculated Jaccard values on the plot.
        for i,j in zip(self.x[-ws:], self.y[-ws:]):
            if i%10 ==0:
               if i > len(self.y)-80: 
                  plt.annotate("{:.4f}".format(j),xy=(i,j), bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3), color='firebrick')
        

        
        # Draw current average
        plt.axhline( y=self.currentAverageJaccard, color='#4169E1', linestyle='dashed', marker='o', markersize=6, label='Current average Jaccard similarity')
        plt.text(x=min(self.x[-ws:]) + 20.5, y=self.currentAverageJaccard + 0.0012, s="Current average Jaccard similarity: " + "{:.7f}".format(self.currentAverageJaccard), color='#4169E1')

        # Draw target expected Jaccard similarity
        if self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET) > 0:
           plt.axhline( y=self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET), color='red', linestyle='solid', marker='o', markersize=6, label=f"Expected Jaccard similarity (target) {self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET)}")
           plt.text(x=min(self.x[-ws:]) + 0.5, y=self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET) + 0.001, s=f'Expected Jaccard similarity = {self.configuration.get("targetexpectedjaccardsimilarity", DEFAULT_JACCARD_SIMILARITY_TARGET)}', color='red')

        # Labels and legends...
        plt.xlabel("# of random pair (= # Jaccard similarities calculated)")
        plt.ylabel("Jaccard similarity")
        plt.legend(loc="upper right", labelcolor='linecolor', borderaxespad=0)

        # TODO: refactor next...
        elapsed = (time.time() - self.startTime)
        if elapsed > 0:
           rate = self.nPairs/elapsed
        else:
           rate = -1
           
        seconds = (self.configuration.get('nsamples', DEFAULT_N_SAMPLES) - self.nPairs)/rate
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        
        
        # Place some info in the textbox
        # TODO: refactor this
        if self.configuration.get('epsilon', -1) < 0:
           textstr = ('n:%d/%d (%.2f%%) at %.2f pairs/sec (approx. %dh%dm%ds)\nU size:%d\nS size:%d\nT size:%d\nMin Jaccard similarity seen:%.5f\nMax Jaccard similarity seen:%.5f\nLast jaccard similarity:%.5f\nAverage Jaccard similarity:%.5f\nMemory usage:%.2f MB'%
                     (self.nPairs, self.configuration.get('nsamples', DEFAULT_N_SAMPLES), 100*self.nPairs/self.configuration.get('nsamples', DEFAULT_N_SAMPLES), rate, hours, minutes, seconds, self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE), self.configuration.get('ssetsize', DEFAULT_S_SIZE), self.configuration.get('tsetsize', DEFAULT_T_SIZE), self.minJaccard, self.maxJaccard, jaccardSimilarity, self.currentAverageJaccard, self.getScriptMemory()/(1024*11024) ))
        else:
           textstr = ('delta:%.7f (ε=%.7f)(%d) at %.2f pairs/sec\nU size:%d\nS size:%d\nT size:%d\nMin Jaccard similarity seen:%.5f\nMax Jaccard similarity seen:%.5f\nLast jaccard similarity:%.5f\nAverage Jaccard similarity:%.5f\nMemory usage:%.2f MB'%
                     (abs(self.currentAverageJaccard - self.configuration.get('targetexpectedjaccardsimilarity', DEFAULT_JACCARD_SIMILARITY_TARGET)), self.configuration.get('epsilon', -1), self.deltaStreak, rate, self.configuration.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE), self.configuration.get('ssetsize', DEFAULT_S_SIZE), self.configuration.get('tsetsize', DEFAULT_T_SIZE), self.minJaccard, self.maxJaccard, jaccardSimilarity, self.currentAverageJaccard, self.getScriptMemory()/(1024*11024) ))

    
        props = dict(boxstyle='round', color="black",  alpha=0.65,)
        textBox = plt.gca().text(0.05, 0.95, textstr,
                             transform=plt.gca().transAxes,
                             fontdict={'family': 'monospace','color':'lime','weight': 'normal','size': 8},
                             verticalalignment='top', bbox=props)

        
        return(None)





    
        
    def nextPair(self):
        '''
           Generates a pair of random S and T sets from the universal set and calculates
           and returns their jaccard similarity.
        '''

        if self.nPairs == 0:
           self.startTime = time.time() 
        
        if self.shouldTerminate():
           self.terminate() 

        
        s, t = self.getSandTSetsRANDOMSAMPLE(self.configuration.get('ssetsize', DEFAULT_S_SIZE),
                                             self.configuration.get('tsetsize', DEFAULT_T_SIZE))

        # Calculate jaccard similarity.
        if self.configuration.get('jaccardmode', 'custom') == 'custom':
           jaccard = self.jaccardSimilarity(s, t)
        elif self.configuration.get('jaccardmode', 'custom') == 'sklearn':   
             jaccard = self.sklearnJaccard(s, t)

        self.nPairs += 1
        

        # Append to lists for plotting and calculate averages.
        # TODO: these lists will grow as the script executes. 
        #       If a long running script is of concern, a different approach should be
        #       implemented: keep only the current window and instead of calling mean() on y
        #       for average Jaccard similarity to calculate the average manually:
        #       keep a sum of all Jaccard similarities and devide it by number of pairs (nPairs).
        self.x.append(self.nPairs)
        self.y.append(jaccard)

        
        self.minJaccard = min(jaccard, self.minJaccard)
        self.maxJaccard = max(jaccard, self.maxJaccard)
        self.currentAverageJaccard = mean(self.y)


        
        # Append to list for housekeeping and logging (e.g. to store all values to the file).
        # This too grows as the script keeps executing.
        # TODO: make keeping these lists optional depending on whether saving to file has bee
        #       chosen.
        newPair = {'timeStamp':getCurrentDateTime(), 'jaccardSimilarity':jaccard}
        if ['sset'] in self.configuration.get('fields_list', []):
           newPair['sset'] = s
        if ['tset'] in self.configuration.get('fields_list', []):
           newPair['tset'] = t

        self.yMeta.append(newPair)

        
        # Returned to doPlot                    
        return(jaccard)
                            


                   
        
    def update(self):
        while True:
              try:
                  yield self.nextPair()
              except KeyboardInterrupt:
                  # TODO: Is the next correct?
                  print('Keyboard interrupt seen. Terminating.')
                  sys.exit(-3)
        



def getCurrentDateTime(tz=None):
    return(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))







######################################################################
#
# Program starts from here
#
######################################################################



def start(cfg={}):


    if cfg.get('ssetsize', DEFAULT_S_SIZE) > cfg.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE):
       clrprint.clrprint(f'[ERROR] S set size ({cfg.get("ssetsize", DEFAULT_S_SIZE)}) cannot be greater than universal set size ({cfg.get("universalsetsize", DEFAULT_UNIVERSAL_SET_SIZE)})', clr='red')
       sys.exit(-4)

    if cfg.get('tsetsize', DEFAULT_T_SIZE) > cfg.get('universalsetsize', DEFAULT_UNIVERSAL_SET_SIZE):
       clrprint.clrprint(f'[ERROR] T set size ({cfg.get("tsetsize", DEFAULT_T_SIZE)}) cannot be greater than universal set size ({cfg.get("universalsetsize", DEFAULT_UNIVERSAL_SET_SIZE)})', clr='red')
       sys.exit(-4)   

    print(f'\n[{getCurrentDateTime()}] Starting with U={cfg.get("universalsetsize", DEFAULT_UNIVERSAL_SET_SIZE)}, S={cfg.get("ssetsize", DEFAULT_S_SIZE)}, T={cfg.get("tsetsize", DEFAULT_T_SIZE)} n={cfg.get("nsamples", DEFAULT_N_SAMPLES)}, e={cfg.get("epsilon", -1)} Expected similarity:{cfg.get("targetexpectedjaccardsimilarity", DEFAULT_JACCARD_SIMILARITY_TARGET)}')
    
    # Initialize plot figure
    fig = plt.figure()

    # Size from inches to pixels
    #size = fig.get_size_inches()*fig.dpi
    
    # figwidth, figheight takes dimensions in inches.
    # Hence the transformation from pixels (specified in command line/configureation) to inches
    fig.set_figwidth((cfg.get('plotwidth', 1024)/fig.dpi))
    fig.set_figheight((cfg.get('plotheight', 480)/fig.dpi))
    
    # Instantiate object to handle generation of random samples and animated plots 
    jsp = JaccardSimilarityPlot(cfg)

    
    # Does the actual animation: update() is called periodically (interval) and the calculated value is returned
    # to doPlot() which does the drawing (and management of plot).
    anim = animation.FuncAnimation(fig, jsp.doPlot, fargs=None, init_func=None, frames=jsp.update(), interval=130, save_count=250)
    plt.tight_layout()
    plt.show()






def main():


    ######################################################################################################
    # Read/set configuration settings. The hierarchy is at follows:
    #    1) Settings from configuration file override default values
    #    2) Command line arguments override settings loaded from configuration file
    ######################################################################################################

    # 3 potential config files are scanned.
    p = configargparse.ArgParser(default_config_files=['ejv.conf', 'jaccard.conf', 'expectedjaccard.conf'], add_help=False)
    p.add_argument('-c', '--configfile', required=False, is_config_file=True, help='config file path')
    

    p.add_argument('-u', '--universalsetsize', type=int, default=DEFAULT_UNIVERSAL_SET_SIZE)
    p.add_argument('-s', '--ssetsize', type=int, default=DEFAULT_S_SIZE)
    p.add_argument('-t', '--tsetsize',  type=int, default=DEFAULT_T_SIZE)
    p.add_argument('-m', '--maxvalue',  type=int, default=DEFAULT_MAX_INT)
    

    # Termination condition related
    # How many samples to generate and calculate their jaccard similarity
    p.add_argument('-n', '--nsamples',  type=int, default=DEFAULT_N_SAMPLES)
    # Stop when the difference of current average to the target value is consistently smaller
    # than an epsilon.
    p.add_argument('-e', '--epsilon',  type=float, default=-1)
    # Consecutive times current average must be smaller than epsilon before quitting.
    p.add_argument('-k', '--deltastreak',  type=float, default=DEFAULT_DELTA_STREAK)

    # Check the distribution of the generated samples?
    p.add_argument('-U', '--uniformitycheck',  action='store_true')
    
    # How to terminate: automatically or wait for user input
    p.add_argument('-A', '--autoterminate', action='store_true')

    
    # Size of window i.e. how many values to show on plot
    p.add_argument('-ws', '--windowsize',  type=int, default=50)

    # Show acutal values on plot using annotations.
    p.add_argument('-V', '--showvalues', action='store_true')
    
    # How to calculate Jaccard distance: natively or using sklearns Multilabelbinarizer that does
    # a one-hot encoding.
    p.add_argument('-j', '--jaccardmode', choices=['custom', 'sklearn'], default='custom')

    # Controls if similarities should be saved into a separate csv file after finishing.
    # File can be specified by -o option 
    p.add_argument('-S', '--savesimilarities', action='store_true')
    # Prefix of csv name to save similarities when savesimilarities has been set
    p.add_argument('-o', '--outputcsvfile', default='jaccardSimilarities')

    
    # Dimensions of plot. In pixels. 
    p.add_argument('-w', '--plotwidth', type=int, default=1024)
    p.add_argument('-h', '--plotheight', type=int, default=480)

    # Displays origin of settings during script startup
    p.add_argument('-O', '--displayconfigorigin', action='store_true')

    # What additional data to save into csv file. For debugging purposes mainly
    # NOTE: currently only sset and tset are supported. Default is none of the sets
    # Add with -f sset -f tset 
    p.add_argument('-f', '--fields-list', nargs='*', action="append", default=[])
    
    

    # The similarity value that is to achieve. Will be shown on the plot as a seprate horizontal line.
    # The idea of the target Jaccard similarity stems from the purpose of this script: to prove *empirically*
    # if the theoretically calculated expected value of exercise  3.1.3 (page 86) in "Managing Massive Dataset" is
    # correct i.e. that the average Jaccard similarity tends to this target value.
    # Some options use this as their base E.g. option epsilon uses distance from this value to determine termination. 
    p.add_argument('-T', '--targetexpectedjaccardsimilarity', type=float, default=DEFAULT_JACCARD_SIMILARITY_TARGET)


    # Debugging purposes
    p.add_argument('-G', '--debug', action='store_true')
    
    knownArgs, _ = p.parse_known_args()
    settings = vars(knownArgs)
    
    if settings['displayconfigorigin']:
       clrprint.clrprint(p.format_values(), clr='yellow')

    # TODO: Check this...how to handle targetexpectedjaccardsimilarity?
    if settings.get('targetexpectedjaccardsimilarity', -1) == -1:
       settings['targetexpectedjaccardsimilarity'] = JaccardSimilarityPlot.theoreticalExpectedValue(settings['universalsetsize'],
                                                                                                    settings['ssetsize'],
                                                                                                    settings['tsetsize'])
    

    # Start generating random samples based on loaded
    # configuration settings.
    start(settings)
    
    



if __name__ == '__main__':
    main()

