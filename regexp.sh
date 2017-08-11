#!/bin/bash
#

echo normalizeing $1
item=$1
tempf1=${item}1.tmp
tempf2=${item}2.tmp
cp ${item}.txt ${tempf1}

# 本文中のリンク削除
sed -e "s/http\:\/\/[0-9a-zA-Z\.\/]*//g" ${tempf1} > ${tempf2}
# 本文中のリンク削除
sed -e "s/http\:\/\/t\.co\/.\{4,10\}//g" ${tempf2} > ${tempf1}
# 本文中のリンク削除
sed -e "s/https\:\/\/t\.co\/.\{4,10\}//g" ${tempf1} > ${tempf2}
# 本文中のsingle quotation削除
sed -e "s/\'//g" ${tempf2} > ${tempf1}
# hashtag削除
sed -e "s/#\w*//g" ${tempf1} > ${tempf2}
# @付きのアカウント部分を削除
sed -e "s/@[0-9a-zA-Z_]*//g" ${tempf2} > ${tempf1}
# カッコ内削除
sed -e "s/【.*】//g" ${tempf1} > ${tempf2}
sed -e "s/～.*～//g" ${tempf2} > ${tempf1}
sed -e "s/－.*－//g" ${tempf1} > ${tempf2}
sed -e "s/（.*）$//g" ${tempf2} > ${tempf1}
sed -e "s/『\(.*\)』.*/\1/g" ${tempf1} > ${tempf2}
sed -e "s/by:.*$//g" ${tempf2} > ${tempf1}
# "削除
sed -e "s/\"//g" ${tempf1} > ${tempf2}
# 文末の空白削除
sed -e "s/\s*$//g" ${tempf2} > tweetdata/regexped/$(basename ${item}).txt

rm -rf ${tempf1} ${tempf2}
