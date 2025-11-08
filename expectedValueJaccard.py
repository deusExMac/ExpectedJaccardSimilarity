##############################################################################
#
# Calculates empirically the expected value of the Jaccard similarity for
# exercise Exercise 3.1.3 (page 86) found in [1]. Attempts to answer the
# question whether the expected value, after several iterations, converges
# to 0.1555 for very specific sizes of the sets S and T (20 and 40
# respectively - although this can easily be changed by modifying some consts).
#
# Does this by repeatedly selecting randomly subsets S and T from the same
# universal set (U) and calculating their jaccard similarity. The
# average of jaccard similarities is calcualted and plotted. Uses animation
# capabilities of matplotlib.
# 
#
# References:
#   1) Leskovec, J., Rajaraman, A., and Ullman, J. D.: Mining of Massive
#      Datasets, Cambridge University Press, 2014. Available http://mmds.org 
#
#
# v0.1/mmt/16112024
##############################################################################



import sys
import random

from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.artist import Artist




# Choosing random values from
# [0, MAX_INT-1]
MAX_INT = 100

# Number of times to draw samples
# and calculate the Jaccard similarity.
# Change this value to change the number of samples
# generated.
MAX_ITERATIONS = 6000

# Sampling parameters
UNIVERSAL_SET_SIZE = 100
S_SIZE = 20
T_SIZE = 40



#######################################################################
# Sampling and similarity related
#######################################################################

# Initilized universal set from which random samples
# will be drawn
def initU(uSize=15):
    return(set(random.sample(range(MAX_INT), uSize)))
    

def jaccardSimilarity(s1, s2):
    return( len(s1.intersection(s2)) / len(s1.union(s2)) )


     
def getSandT(u=None, sizeS=20, sizeT=40):
    S = list(u)
    random.shuffle(S)
    
    T = list(u)
    random.shuffle(T)
    
    return(set(S[:sizeS]), set(T[:sizeT]))


#######################################################################
# Animated plot related
#######################################################################


def plotDictionary(d):
    plt.clf()
    plt.bar(range(len(d)), list(d.values()), align='center')
    plt.xticks(range(len(d)), list(d.keys()), rotation=65, ha='right')
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.show()  



def update():
    global nIter, universalSet, jaccardScores
    
    s, t = getSandT(universalSet, S_SIZE, T_SIZE)
    nIter += 1
    
    jaccard = jaccardSimilarity(s, t)
    
    return(nIter, jaccard)




def animate(args):

    global textBox, allSamples

    if MAX_ITERATIONS > 0:
       if nIter > MAX_ITERATIONS:
          wait = input("\n\nFinished gracefully. Press enter to continue...")
          sys.exit(0)
          
    
    # Clear plot
    plt.clf()
    plt.title('Expected value of jaccard similarity')
    
    x.append(args[0])
    y.append(args[1])    
    plt.plot(x, y, color='g', marker='o', linestyle='dotted', markersize=1,  label='Jaccard similarity of random sample')
    plt.axhline( y=sum(y)/(args[0]), color='blue', linestyle='dotted', marker='o', markersize=6, label='Current average')
    plt.axhline( y=0.1555, color='red', linestyle='dashdot', marker='o', markersize=6, label='Value 0.1555')
        
    plt.xlabel("# random samples")
    plt.ylabel("Jaccard similarity")
    plt.legend( loc="upper right", borderaxespad=0)


    # Textbox with some info...
    font = {'family': 'monospace','color':  'lime','weight': 'normal','size': 8,}
    
    # Remove textBox before creating a new one
    #if textBox is not None:
    #   Artist.remove(textBox)

       
    textstr = ('n:%d/%d (%.2f%%)\nUniversal set size:%d\nS size:%d\nT size:%d\nLast jaccard similarity:%.5f\nAverage jaccard similarity:%.5f'%
               (nIter, MAX_ITERATIONS, 100*nIter/MAX_ITERATIONS, UNIVERSAL_SET_SIZE, S_SIZE, T_SIZE, args[1], sum(y)/(args[0])))
    
    props = dict(boxstyle='round', color="black",  alpha=0.7,)
    textBox = plt.gca().text(0.05, 0.95, textstr,
                             transform=plt.gca().transAxes,
                             fontdict={'family': 'monospace','color':  'lime','weight': 'normal','size': 8},
                             verticalalignment='top', bbox=props)
    return(None)





def frames():
    while True:
        try:
          yield update()
        except KeyboardInterrupt:  
          print('Keyboard interrupt seen. Terminating.')
          sys.exit(-3)







######################################################################
#
# Program starts from here
#
######################################################################

# Some globals. Makes things a little bit easier.
# But, sorry about this.
universalSet = None
nIter = 0
textBox= None


# data on x axis (number of iteration)
x = []

# data on y axis (jaccard similarity)
y = []





def main():

    global universalSet
    
    universalSet = initU(UNIVERSAL_SET_SIZE)
    print(universalSet)

    # Initialize plot figure
    fig = plt.figure()

    # Size from inches to pixes
    size = fig.get_size_inches()*fig.dpi

    # Increase default figure width by 60% (inches)
    fig.set_figwidth(fig.get_size_inches()[0]+fig.get_size_inches()[0]*0.6)


    # Let's go...
    # TODO: check if cache_frame_data needs to be set to False (instead or setting the save_count)
    anim = animation.FuncAnimation(fig, animate, frames=frames, interval=20, save_count=250)
    plt.tight_layout()
    plt.show()




if __name__ == '__main__':
    main()

