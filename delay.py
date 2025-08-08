
# %%

import random
import pandas as pd 

import matplotlib.pylab as pylt
pylt.rcParams['figure.dpi'] = 200
import seaborn as sns
import matplotlib.pyplot as plt 
%matplotlib inline

from sudulunu.helpers import pp, dumper

# %%

def delayer(disto = 'mid'):
    bottom = 0
    top = 100
    mid = 50

    mode = mid

    if disto == 'every':
        return True

    if disto == 'mid':
        mode = mid
    elif disto == 'low':
        mode = top * 0.25
    elif disto == 'high':
        mode = top * 0.75

    if random.triangular(bottom, top, mode) < mid:
        return True
    else:
        return False


# %%

records = []

for i in range(0, 100):

    for thingo in ['low', 'mid', 'high']:
        # record[thingo] = delayer(thingo)
        
        record = {"Variable": thingo, 'Value': delayer(thingo)}
        # donner = delayer(thingo)


        records.append(record)

cat = pd.DataFrame.from_records(records)

pp(cat)


# %%

# sns.kdeplot(cat, x='Value', hue='Variable')
# sns.countplot(cat, x='Value', hue='Variable')

# %%


if delayer('high'):
    print('Hi')
else:
    print("No")
# %%

if delayer('every'):
    print("Hihi")
# %%
