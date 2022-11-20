import pandas as pd

df = pd.read_csv("/Users/admin/Downloads/seng480b/Diff size data/prlist.txt", sep=",")
df["sloc"]=df['Insertions']+df['Deletions']+df['Modifications']

def turkey_outlier(df, column, whisker_width=1.5):
    # Calculate Q1, Q2 and IQR
    q1 = df[column].quantile(0.25)                 
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    # Apply filter with respect to IQR, including optional whiskers
    filter = (df[column] >= q1 - whisker_width*iqr) & (df[column] <= q3 + whisker_width*iqr)
    return df.loc[filter]                                                     

# Example for whiskers = 1.5, as requested by the OP

display(df)
display(df.describe())
df = turkey_outlier(df, 'Merge time minutes', whisker_width=1.5)
df = turkey_outlier(df, 'sloc', whisker_width=1.5)
display(df)
df.describe()

import math
import numpy as np
day=df["Merge time minutes"]/60
day=pd.to_numeric(day, downcast='integer').apply(np.ceil)
sloc=pd.DataFrame(day)
sloc["sloc"]= df['Insertions']+df['Deletions']+df['Modifications']
display(sloc)

import matplotlib.pylab as plt
sloc=sloc.sample(n=1000,random_state=3)
plt.figure(figsize=(8,8))
plt.axes(xscale='log', yscale='log')

plt.scatter(sloc['sloc'], sloc['Merge time minutes'],s=5)
plt.xlabel('sloc')
plt.ylabel('Merge time in hours')

pull=pd.DataFrame()
pull= df.copy()
pull.drop(["PR ID",])
pull=pull.groupby(["Language"]).describe()[[]]
display(pull)