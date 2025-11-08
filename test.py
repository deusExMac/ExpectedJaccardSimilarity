


import sys
import random

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.artist import Artist

from sklearn.metrics import jaccard_score

from sklearn.preprocessing import LabelBinarizer





def oneHot(cl):
    return(pd.get_dummies(cl, dtype=int))


def jaccardSimilarity(s1, s2):
    return( len(s1.intersection(s2)) / len(s1.union(s2)) )




data = {
    'A': [1, 4],
    'B': [8, 2],
    'C': [3, 6]
}

df = pd.DataFrame(data)
origData = df.copy()
print(df)

all_categories = set(cat for cat in df['A'] )
all_categories.update( set(cat for cat in df['B'] ))
all_categories.update( set(cat for cat in df['C'] ))
labels = list(all_categories)
#["first", "second", "third"]

from sklearn.preprocessing import LabelBinarizer
lb = LabelBinarizer()
lb.fit(labels)
dt = [1,2,3]
res=lb.transform(dt)
print(labels)
print(res)

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score
y_true = [['a','b','c']]
y_pred = [['a','c','b']]

binarizer = MultiLabelBinarizer()

# This should be your original approach
#binarizer.fit(your actual true output consisting of all labels)

# In this case, I am considering only the given labels.
binarizer.fit(y_true)



import sys
sys.exit(-3)

colHeaders = list(df.columns.values)

for col in colHeaders:
    print(col)
    df = pd.concat([df, pd.get_dummies(df[col], dtype=int)], axis=1)
    df = df.drop(col, axis=1)

#df = pd.concat([df, pd.get_dummies(df['A'], dtype=int)], axis=1)
#df = pd.concat([df, pd.get_dummies(df['B'], dtype=int)], axis=1)
#df = pd.concat([df, pd.get_dummies(df['C'], dtype=int)], axis=1)
#df = df.drop('A', axis=1)
#df = df.drop('B', axis=1)
#df = df.drop('C', axis=1)

print(df)

jSim = jaccardSimilarity( set(origData.iloc[0,:]), set(origData.iloc[1,:]))
print('Custom jaccard:', jSim)

skLearnJaccard = jaccard_score(list(df.iloc[0,:]), list(df.iloc[1,:]), average='binary')
print('sklearn jaccard:', skLearnJaccard)




import sys
sys.exit(-2)





all_categories = set(cat for cat in df['A'] )


all_categories.update( set(cat for cat in df['B'] ))
#print(all_categories)

all_categories.update( set(cat for cat in df['C'] ))
print(all_categories)

# TODO: NExt is wrong...
for category in all_categories:
    df[category] = df['A'].apply(lambda x: 1 if category == x else 0)

for category in all_categories:
    df[category] = df['B'].apply(lambda x: 1 if category == x else 0)
for category in all_categories:    
    df[category] = df['C'].apply(lambda x: 1 if category == x else 0)
print(df)
    
'''
for category in all_categories:
    df[category] = df['Categories'].apply(lambda x: 1 if category in x else 0)
'''
