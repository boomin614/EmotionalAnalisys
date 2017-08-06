# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 13:08:58 2017

@author: boomin
"""

import pandas as pd
import pickle

class iopkl:

  def __init__(self):
    self.c = self

  def readpkl(self, path):
    with open(path, 'rb') as f2:
      return pickle.load(f2)

  def savepklfile(self, df, wfilename):
    with open(wfilename,'wb') as f1:
      pickle.dump(df,f1)

  def readData(self, datafile):
    rdata = pd.read_csv(
      datafile,
      sep = "\t",
      #header=None,
      header=0,
      parse_dates=[0],
      engine='python',
      error_bad_lines=False,
      encoding="utf-8"
    )
    return rdata


if __name__ == '__main__':
  print("iopkl")
