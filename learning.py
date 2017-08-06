# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:26:59 2017

@author: boomin
"""
import fasttext as ft
import argparse

# 実行引数の受け取り
parser = argparse.ArgumentParser(description="学習データを学習し、学習モデルを作る")
parser.add_argument('input', type=str, help="入力ファイルへのPath(必須)")
parser.add_argument('output',type=str, help="出力ファイルへのPath(必須)")
args = parser.parse_args()

# 学習
classifier = ft.supervised(args.input, args.output, dim=400, lr=0.05, epoch=200, thread=6)

# Properties
result = classifier.test(args.input, 2)
print("result.nexamples", result.nexamples) # Number of test examples
print("result.precision", result.precision) # Precision at one
print("result.recall",    result.recall)    # Recall at one
print("result.F-measure", 2*result.recall*result.precision/(result.recall+result.precision))    # F-measure

