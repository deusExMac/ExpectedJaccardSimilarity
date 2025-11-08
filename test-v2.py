


import sys
import random

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.artist import Artist

from sklearn.metrics import jaccard_score

from sklearn.preprocessing import LabelBinarizer, MultiLabelBinarizer
import clrprint

MAX_INT = 100

def initU(uSize=15):
    return(set(random.sample(range(MAX_INT), uSize)))


def getSandT(u=None, sizeS=20, sizeT=40):

    if (sizeS > len(u)) or (sizeT > len(u)):
       print('[WARNING] subset larger than superset')
       
    S = list(u)
    random.shuffle(S)
    
    T = list(u)
    random.shuffle(T)
    
    clrprint.clrprint('\nS=', set(S[:sizeS]), '\nT=', set(T[:sizeT]), sep='', clr='yellow')
    return(set(S[:sizeS]), set(T[:sizeT]))



def jaccardSimilarity(s1, s2):
    return( len(s1.intersection(s2)) / len(s1.union(s2)) )






print("++++++++++++++++++++++++++++++++++++++++++++++++++")

universalSet = initU(100)
#print('UniversalSet:', universalSet)

sm=[]
sksm=[]
for i, j in enumerate(range(6500)):
    s, t = getSandT(universalSet, 20, 40)

    mlb = MultiLabelBinarizer()
    vec1 = list(s)#[random.randint(10, 2009),random.randint(10, 2009),random.randint(10, 2009)]
    vec2 = list(t)#[random.randint(10, 2009),random.randint(10, 2009),random.randint(10, 2009)]

    mlf=mlb.fit_transform([set(vec1), set(vec2)])


    sList=mlf[0,:].tolist()
    tList=mlf[1,:].tolist()


    jSim = jaccardSimilarity(s, t)
    print('Custom jaccard:', jSim)

    skjSim = jaccard_score(sList, tList, average='binary')
    print('sklearn jaccard:', skjSim)

    if jSim != skjSim:
       print(f'Uneven Jaccard distances: {jSim}, {skjSim}. Terminating.')
       sys.exit(-3)
       
    sm.append(jSim)
    avg = sum(sm)/(i+1)

    sksm.append(skjSim)
    skavg = sum(sksm)/(i+1)
    print(f'\t{i}) average:{avg:.5f} skaverage:{skavg:.5f}')






