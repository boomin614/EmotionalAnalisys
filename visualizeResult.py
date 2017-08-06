# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:26:59 2017

@author: boomin
"""

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
import datetime
import argparse
from iopkl import iopkl

# 入出力モジュール読み込み
p = iopkl()

# 実行引数の受け取り
parser = argparse.ArgumentParser(description="MeCabで分かち書きを行うためのスクリプトです")
parser.add_argument('input', nargs="+", type=str, default="", help="評価対象のデータ(必須)")
args = parser.parse_args()

# 描画対象データファイルを読み込み
tardf = pd.DataFrame()
for fname in args.input:
  res = p.readpkl(fname)["posibility"].astype(float)
  tardf = tardf.join(res.to_frame(name=fname), how='outer')

# 集約した描画対象データファイルを保存
p.savepklfile(tardf, "drawdata.pkl")
#tardf = p.readpkl("drawdata.pkl")

import re
def getAccount(fn):
  text = re.sub(r'result_w_', "", fn)
  text = re.sub(r'\.\w{3}$', "", text)
  return text


def drawPredictResult(df,title):
  plt.close('all')
  fsize=28
  plt.rcParams["font.size"] = fsize
  plt.figure(figsize=(28, 16))
  plt.title('{}'.format(title))
  #
  for i, col in enumerate(df.columns):
    color = cm.brg(i/len(df.columns))
    #plt.plot(df[col],label="@"+col, linestyle="dashed", c=color)
    plt.plot(df[col].resample('1W').mean(), linewidth=1, c=color, label="@"+col)
    plt.plot(df[col].resample('1M').mean(), linewidth=3, c=color, label=None, linestyle="dashed")
  #
  ax=plt.gca()
  handles, labels = ax.get_legend_handles_labels()
  labels  = [getAccount(item) for i, item in enumerate(labels) if i%2!=0]
  handles = [item for i, item in enumerate(handles) if i%2!=0]
  plt.legend(handles, labels, loc="lower left", ncol=1, fontsize=fsize)
  plt.ylabel("-1 : negative <------> positive : +1", fontsize=fsize)
  #plt.ylabel(label[1], fontsize=fsize)
  #
  plt.xlim([datetime.date( 2017, 4, 1 ), datetime.date( 2017, 7, 24 )])
  plt.ylim([-1, 1])
  plt.savefig('{}.png'.format(title), bbox_inches='tight')

title = "Time Series Variation of Emotional Analysis Results from Tweet Data {}".format(args.input[0])
drawPredictResult(tardf,title)

