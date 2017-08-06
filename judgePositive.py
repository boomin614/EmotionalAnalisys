# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:26:59 2017

@author: boomin
"""
# -*- coding: utf-8 -*-
import fasttext as ft
import os
import pandas as pd
from iopkl import iopkl
import argparse

# 実行引数の受け取り
parser = argparse.ArgumentParser(description="MeCabで分かち書きを行うためのスクリプトです")
parser.add_argument('input', type=str, help="評価対象のデータ(必須)")
parser.add_argument('model', type=str, help="学習モデル(必須)")
args = parser.parse_args()

# 入出力モジュール読み込み
p = iopkl()

name,ext = os.path.splitext( os.path.basename(args.input) )
# 評価対象データの読み込み
if ext==".pkl":
  data = p.readpkl(args.input)
elif ext==".tsv":
  data = p.readData(args.input)
else:
  print("cann't read data")
  exit(1)

# 学習モデルの読み込み
classifier = ft.load_model(args.model)

res = pd.DataFrame()
for key, tweet in data.iterrows():
  try:
    if(len(tweet)!=3 or len(tweet[2])<1):
      continue
    #
    words = tweet[2]
    #
    estimate = classifier.predict([words], k=2)
    score = classifier.predict_proba([words], k=2)
    #
    lab = ""
    score = score[0][0][1]
    if estimate[0][0] == "__label__1,":
      lab = "p"
    elif estimate[0][0] == "__label__2,":
      lab = "n"
      score *= -1
    #
    tmp = pd.DataFrame([tweet[0], lab, score, tweet[2]], index=["date", "label", "posibility", "tweet"])
    res = res.append(tmp.T)
    #print("{}\t{}\t{:.5f}\t{}".format(tweet[0], lab, score, tweet[2]))
  #
  except:
    continue


res.set_index(["date"],inplace=True)
res.index = res.index.tz_localize('UTC').tz_convert('Asia/Tokyo')
res["posibility"].astype(float)

 
refile = "result_" + name
p.savepklfile(res, refile+".pkl")
res.to_csv(refile+".tsv", sep='\t')
