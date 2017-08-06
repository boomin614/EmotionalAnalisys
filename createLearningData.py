# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 08:40:07 2017
URL: https://foolean.net/p/576

@author: boomin
"""

from Mecab2 import Mecab2, Regexp
import argparse
import os.path
from iopkl import iopkl

# 実行引数の受け取り
parser = argparse.ArgumentParser(description="MeCabで分かち書きを行う")
parser.add_argument('input', type=str, help="入力ファイルへのPath(必須)")
parser.add_argument('-n', '--col',    nargs="+", type=int, default=[0], help="形態素解析対象のカラム番号")
parser.add_argument('-o', '--output', nargs=1, type=str, default="", help="出力ファイルへのPath(Default:out.txt)")
args = parser.parse_args()

p = iopkl()
m = Mecab2(target=["名詞","動詞","形容詞","副詞"])
c = Regexp()

def getline(line):
  if not isinstance(line,str):
    return ""
  # mei対ソ解析の前処理：推奨される文字種に変換
  text = c.normalize(line)
  # 形態素解析
  text = m.wakati(text)
  return text

# ファイル読み込み
data = p.readData(args.input)

if max(args.col) > len(data.columns)-1:
  print("error")
  exit()

# 指定された列を対象に形態素解析
for cn in args.col:
  data.ix[:,cn] = data.apply(lambda x: getline(x[cn]), axis=1)


# 出力ファイル名決定
if len(args.output)>0:
  print(args.output)
  name,ext = os.path.splitext( os.path.basename(args.output) )
  fout1  = args.output
  fout2  = "w_"+name+".pkl"
else:
  name,ext = os.path.splitext( os.path.basename(args.input) )
  fout1  = "w_"+name+".tsv"
  fout2  = "w_"+name+".pkl"

# 結果の出力
data.to_csv(fout1, sep="\t", encoding="utf-8", index=False, header=False)
p.savepklfile(data, fout2)
