# はじめに
日本語のテキストマイニングを、[Facebook FastText](https://research.fb.com/fasttext/)で実際にやってみる。  
souce codeはすべて[ここから](https://github.com/facebookresearch/fastText)取得できます。  
build方法なども書いてある。  


今回は、Twitterのつぶやきの感情分析を行い、  
そのつぶやきがポジティブなのかネガティブなのか、それを判定してみようと思う。  
なお、今回はちょっと長文になる。


# 前提

すでに前の記事で以下について投稿済みなので、そちらを事前に見ておくと、スムーズかと思います。

1. [環境構築](http://boomin.yokohama/archives/619)
  - Mecabやfasttextなどの導入手順
1. [日本語の前処理](http://boomin.yokohama/archives/634)
  - 形態素解析
  - テキストマイニングの精度向上させるコツ
  - それを実現するためのライブラリとその使い方

# 手順

## 1. twitterからデータを入手する
以下のように、[getTweet.py](getTweet.py)に引数を与えて実行すれば取得できる。

```bash
python getTweet.py 対象アカウント
```

対象アカウントとして、引数に複数指定できる。


### 1.1 教師データの入手
学習データの準備として、twitterでポジティブ名言とネガティブ名言を取得する。  
ポジティブ名言として取得したアカウント、ネガティブ明言として取得したアカウントの一覧は以下の通り。

| 分類      | アカウント  | アカウント数
|:----------|:-----------|----:|
| ポジティブ | positive_bot3 posi_tive_sp_ kami_positive positivekk_bot maemukikotoba1 Plus_bot heart_meign bot10586321 | 8 |
| ネガティブ | n_siko nega_bot Mostnegative cynicalbot UnluckyBot Antinatalismbot | 6 |

教師データとする、ネガティブ発言を集めるのが悩ましかった。そりゃそうか。  
みんな、ネガティブなことなんて、聞きたいくないし。

以下のように、shellからpython codeを呼び出して、twitterデータを収集する。

```bash
#!/bin/bash
#
# ポジティブ名言アカウントとネガティブ名言アカウントを配列にしておいて、一気に取得する
P_ARRAY=(positive_bot3 posi_tive_sp_ kami_positive positivekk_bot maemukikotoba1 Plus_bot heart_meign bot10586321)
N_ARRAY=(n_siko nega_bot Mostnegative cynicalbot UnluckyBot Antinatalismbot)

echo get tweet data
for item in ${P_ARRAY[@]} ${N_ARRAY[@]}; do
  echo "get tweet data: "$item
  python getTweet.py $item
  sleep 3
done
```

この後も使うため、ポジティブなアカウントとネガィテブなアカウントを、  
それぞれ **P_ARRAY** 、**N_ARRAY** という配列に入れておく。



どんな処理をしているのか気になる場合は、[getTweet.py](getTweet.py)の中身を見てください。  
positive_bot3.n_siko.txt、。。。といった、**アカウント名.txt** というテキストファイルが作成される。


ファイルの中身は、こんな感じになっているはず。
これは、**「positive_bot3.txt」** の中身の一部です。
```
date	user	tweet
Fri Aug 04 07:19:03 +0000 2017	positive_bot3	剣は折れた。だが私は折れた剣の端を握ってあくまで戦うつもりだ。～ド・ゴール～
Fri Aug 04 05:19:05 +0000 2017	positive_bot3	あきらめたらそこで試合終了だよ ～安西監督～
Fri Aug 04 01:19:05 +0000 2017	positive_bot3	人生の目的は悟ることではありません。生きるんです。人間は動物ですから。～岡本太郎～
Thu Aug 03 23:19:07 +0000 2017	positive_bot3	他人の後ろから行くものは、けっして前進しているのではない。 ～ロマン・ロラン～
Thu Aug 03 13:19:04 +0000 2017	positive_bot3	過ぎたことを悔やんでも、しょうがないじゃないか。目はどうして前についていると思う？前向きに進んでいくためだよ。　　～　ドラえもん～
Thu Aug 03 11:19:05 +0000 2017	positive_bot3	知ってた？スタバで出来る無料のカスタマイズおすすめ５選！
Thu Aug 03 09:19:03 +0000 2017	positive_bot3	やる前に負ける事考えるバカいるかよ！ ～アントニオ猪木～
Thu Aug 03 07:19:03 +0000 2017	positive_bot3	人生３万日しかない～中川翔子～
Thu Aug 03 05:19:07 +0000 2017	positive_bot3	10年後にはきっと、せめて10年でいいからもどってやり直したいと思っているのだろう。 今やり直せよ。未来を。10年後か、20年後か、50年後からもどってきたんだよ今。～２ちゃんねる就職板～
Thu Aug 03 03:19:04 +0000 2017	positive_bot3	発明は恋愛と同じです。苦しいと思えば苦しい。楽しいと思えばこれほど楽しいことはありません。～本田宗一郎～
```



### 1.2 評価対象データの入手
分析対象データもtwitterのつぶやきなので、合わせて取得しておく。  
方法は、教師データとまったく同様。

| 分類      | アカウント  | アカウント数
|:----------|:-----------|----:|
| 個人的フォロワー | boomin614 shimasho yutokiku karen529mm iwasaki_p toosee_spidy | 6 |
| アニメのキャラセリフ他 | matsuoka_shuzo shinji0606_bot ayano0515 | 3 |
| 日経関連アカウント | nikkei nikkeilive nikkeivdata nikkeistyle nikkeiDUAL nikkei_WOL nikkei_ent Nikkei_TRENDY | 9 |


```bash
# 対象アカウントを配列にしておいて、一気に取得する
#!/bin/bash
#
T_ARRAY=(boomin614 shimasho yutokiku karen529mm iwasaki_p toosee_spidy)
A_ARRAY=(matsuoka_shuzo shinji0606_bot ayano0515)
NIKKEI=(nikkei nikkeilive nikkeivdata nikkeistyle nikkeiDUAL nikkei_WOL nikkei_ent Nikkei_TRENDY)
echo get tweet data
for item in ${T_ARRAY[@]} ${NIKKEI[@]}; do
  echo "get tweet data: "$item
  python getTweet.py $item
  sleep 3
done
```

こうすることで、boomin614.txt、shimasho.txt、。。。といった、**アカウント名.txt** というテキストファイルが作成される。

ファイルの中身は、こんな感じになっているはず。
これは、**「nikkei.txt」** の中身の一部です。
```
date	user	tweet
Fri Aug 04 07:52:02 +0000 2017	nikkei	伊藤忠商事ＣＦＯ、中国経済「思っている以上に順調」
Fri Aug 04 07:13:00 +0000 2017	nikkei	バルセロナからパリ・サンジェルマンに移籍するサッカーの #ネイマール。巨額移籍を動かしたカタールマネーの底力に迫りました。
Fri Aug 04 07:10:03 +0000 2017	nikkei	ネイマール獲得　カタールマネーの底力
Fri Aug 04 07:10:02 +0000 2017	nikkei	海外旅行「はしか」にご注意　欧州で流行、厚労省呼び掛け
Fri Aug 04 06:58:02 +0000 2017	nikkei	民進・細野氏、離党の意向表明　「新党つくる決意」
Fri Aug 04 06:55:02 +0000 2017	nikkei	日経平均続落、終値は76円安の１万9952円
```



## 2. 入手したデータの前処理

### 2.1 学習データの前処理
前処理としてやらないといけないことは、だいたい以下の通りです。

1. 不要データの削除
1. 規格化、分かち書き、品詞フィルタ
  - 学習データとして、ノイズ低減のために、規格化と品詞やストップワードによるフィルタリングが必要
  - さらに、日本語の場合、単語で分かち書きする必要あり
1. 学習対象データの抽出と連結、
1. 学習対象データのラベル付け
1. 重複データの削除


不要データの削除は、形態素解析する前のほうが都合がいいこともあるし、  
あとのほうが都合がよいこともあるでしょう。  
データごとに、そこは適当に処理をしてください。


##### 2.1.1 不要データの削除（お好み）
分析において、その他削除したい単語などがある場合は、その処理を行う。

例えば、今回の場合、twitterのデータを分析対象としている。  
そのため、内容によっては、以下のような文字列は、削除したくなるかもしれない。  


* Hashtagの削除
  - hashtagそのものは、文章の流れとは関係ないと判断して削除
* 引用元を削除
  - （人名）となっているような部分は、文章の流れではないと仮定して削除
  - アカウントによって表現は異なるが、例えば以下のようなケースがある。
    + ** （\w*） ** や、 ** \(\w*\) **
    + ** ～\w*～ ** とか
* リプライを削除
  - botのアカウントを使って、管理者が呟いているようなものは、名言じゃないと判断して削除する
  - ** @\.* ** とか

こうした上記のような文字列は、学習データとしてふさわしくないとして、削除する。  
実際には、アカウントというか、対象データの中身を見て、しかるべき文字列を削除する。


ここでは、いちいちアカウントごとに一つずつやるのも面倒なので、正規表現で一括処理することにします。  

```shell
$ regexp.sh ${P_ARRAY[@]} ${N_ARRAY[@]} ${T_ARRAY[@]} ${A_ARRAY[@]} ${NIKKEI[@]}
```

どんな処理をしているのかは、[regexp.sh](regexp.sh)の中身を見てください。  
sed使って正規表現で一気に該当部分を削除しているだけ。  
これを実行すると、元ファイルが書き換えられる。  
それが嫌なら、元のtweetデータはバックアップを取っておいてください。


#### 2.1.2 学習データの規格化、分かち書き、品詞フィルタ
こんな感じで、[createLearningData.py](createLearningData.py)に引数を指定して実行する。


```bash
echo convert tweet data to wakati
for item in ${P_ARRAY[@]} ${N_ARRAY[@]}; do
  echo "converting data: "$item
  python createLearningData.py ${item}.txt -n 2
done
```

-nオプションで、対象のカラム番号を指定する。  
最初のカラム番号が、0から始まることに注意する。  
すなわち、ここで2をしているということは、3番目のカラムとなる。

以下のような2つのファイルが出力される。

* **w_positive_bot3.tsv**
* w_positive_bot3.pkl

学習データの前処理としては、以降、拡張子が「tsv」のものを使用する。

このコマンドの結果、以下のような内容のファイルが得られる。
これは、**w_positive_bot3.tsv** の内容となる。
```
Fri Aug 04 23:19:06 +0000 2017	positive_bot3	自分 立つ いる  深い 掘る そこ キット 泉 湧く でる
Fri Aug 04 13:19:08 +0000 2017	positive_bot3	自分 考える た  生きる ない なる ない そう だ ない 自分 生きる た  考える しまう
Fri Aug 04 11:19:05 +0000 2017	positive_bot3	お前 いつか 出会う 災い おまえ おろそか する た 時間 報い だ
Fri Aug 04 09:19:04 +0000 2017	positive_bot3	やる 前 負ける  考える バカ いる かよ
Fri Aug 04 07:19:03 +0000 2017	positive_bot3	剣 折れる た だ 私 折れる た 剣 端 握る あくまで 戦う  だ
Fri Aug 04 05:19:05 +0000 2017	positive_bot3	あきらめる た 試合終了 だ
Fri Aug 04 01:19:05 +0000 2017	positive_bot3	人生の目的 悟る  だ ある ます ん 生きる  です 人間 動物 です
Thu Aug 03 23:19:07 +0000 2017	positive_bot3	他人 後ろ 行く  けっして 前進 する いる  だ ない
Thu Aug 03 13:19:04 +0000 2017	positive_bot3	過ぎる た  悔やむ しょうが ない ない 目 どうして 前 つく いる 思う 前向き 進む いく  だ
Thu Aug 03 09:19:03 +0000 2017	positive_bot3	やる 前 負ける  考える バカ いる かよ
Thu Aug 03 07:19:03 +0000 2017	positive_bot3	人生 3 万 日 ない
```

ちゃんと、形態素解析され、基本形に変換され、そしてストップワード（記号などの除外）や  
品詞フィルタ（ここでは名詞、形容詞、副詞、動詞、助動詞のみ）が効いている。  
ここの処理の詳しい中身は、[日本語の前処理](http://boomin.yokohama/archives/634)を読んでください。



一般的には、助動詞は除外することが多い。  
しかし、今回はネガポジの感情判定することが目的。  
否定を検知するために、意図的に助動詞を分析対象として選択している。  
ただ、これが良かったのか悪かったのかはわからない。


##### 2.1.3 対象データの抽出と連結、そしてラベル付け
まず、tweetデータ以外は不要なので、それだけを取り出す。  
そしてポジティブなアカウントのつぶやきだけ、ネガティブなアカウントのつぶやきだけでまとめる。  
ついでに、正解ラベルも付けておく。  


以下のスクリプトで処理している内容：

1. 対象ファイルの3列目が空じゃないものだけを対象とする
1. 3列目だけを抽出
1. 抽出された文章の先頭に、ラベルを付ける。

ここでは、

* positiveな文章の先頭に **\_\_label\_\_1,**
* negativeな文章の先頭に **\_\_label\_\_2,**

を付ける。  
これは、FastTextの仕様というかルール。  
デフォルトでは、ラベルには\_\_label\_\_を付けておく必要がある。



各ファイルの先頭行には、「date	user	tweet」というヘッダがついている。  
そこで、awkで1行読み飛ばすオプションを付けておく。


```bash
rm -rf label_positive.tsv &&
for item in ${P_ARRAY[@]}; do
  echo $item
  awk -F"\t" 'NR>1 {if ( $3!~/^$/ ) print $3}' w_${item}.tsv | sed -e "s/^/__label__1, /g" >> label_negaposi.tsv
done
```

上記のawkを使ったscriptで以下のような中身の **「label_negaposi.tsv」** が得られるはず。

```
__label__1, 自分 考える た  生きる ない なる ない そう だ ない 自分 生きる た  考える しまう
__label__1, お前 いつか 出会う 災い おまえ おろそか する た 時間 報い だ
__label__1, やる 前 負ける  考える バカ いる かよ
__label__1, 剣 折れる た だ 私 折れる た 剣 端 握る あくまで 戦う  だ
__label__1, あきらめる た 試合終了 だ
__label__1, 人生の目的 悟る  だ ある ます ん 生きる  です 人間 動物 です
__label__1, 他人 後ろ 行く  けっして 前進 する いる  だ ない
__label__1, 過ぎる た  悔やむ しょうが ない ない 目 どうして 前 つく いる 思う 前向き 進む いく  だ
```


ネガティブ発言も同様。  
ただし、ネガティブ名言の場合は、ラベルを **__label__2** としていることに留意。
また、教師データとして1つのファイルにまとめたいので、ポジティブ発言で処理したファイル「label_negaposi.tsv」に、追記していることに留意。


```bash
for item in ${N_ARRAY[@]}; do
  echo $item
  awk -F"\t" 'NR>1 {if ( $3!~/^$/ ) print $3}' w_${item}.tsv | sed -e "s/^/__label__2, /g" >> label_negaposi.tsv
done
```


##### 2.1.4 重複データの削除
元ネタがbotなので、同じセリフを繰り返しつぶやいている。そのため、この重複を排除しないと、  
 ** 特定の繰り返し回数が多い** 発言が、よりポジティブ（ネガティブ）なもの、として学習されてしまう。  
そこで、重複したセリフを排除する。

```shell
sort -f label_negaposi.tsv -b | uniq > traindata.tsv
```

ただ、これも物は考えようで、繰り返しが多いものは、  
よりポジティブだったりネガィテブだったりと考えることもできる。  
ここをどう考えて教師データを作るか、データのクレンジングはいつも悩ましい。



### 2.2 評価対象データの前処理
学習データと同様、評価対象データも同様に、前処理を行う。  
具体的な内容は、基本的に一緒だが、ラベル付は不要。  
教師データより、することは少ない。

1. 規格化、分かち書き、品詞フィルタ
1. 不要データの削除


```shell
echo convert tweet data to wakati
for item in ${T_ARRAY[@]} ${A_ARRAY[@]} ${NIKKEI[@]}; do
  echo "converting data: "$item
  python createLearningData.py ${item}.txt -n 2
done
```

-nの引数で、対象カラム番号を指定する。複数指定可。  
アカウント数だけファイルがあるはずなので、とにかく処理する。

上記のようなコマンドを打鍵した場合、以下のような2つの結果ファイルが作られる。

* w_boomin614.tsv
* **w_boomin614.pkl**

拡張子が「pkl」のものを、後続の処理で使用する。


### 2.3 これまでの処理結果の確認

ここまで、教示データと評価対象データに対して、前処理を行ってきました。  
その結果、以下のような内容のファイルが得られているか、確認しておきましょう。  

* 教師データ **[traindata.tsv]**
```
__label__1, する てる まに もっと 未来へ 目 むける ない ふりかえる いる ない 前 見る 進む ない
__label__1, だ ポジティブ だ 意味 づける する そこ ポジティブ だ 影響 受け取る  できる
__label__1, ちゃんと 生きること 人生  一 度 訪れる ない
__label__1, 起こる 人 優しい する なさる それ 後々 あなた 財産 なる
__label__1, 死ぬ 出端 ない  生きる 問題 だ  だ
__label__1, 試す た 道 外れる た  近道 遠回り する た 全て 今 自分 繋がる いる 思う
__label__1, 重ねる  とんでも ない  行く ただ ひとつ 道
__label__1, 寝る 忘れる さ
__label__1, 人生 これ だ いい 考える いける ない そう 思う た 瞬間 進歩 止まる 置く いく れる だ う
__label__1, 友人 僕 当り前 やる いる  俺 到底 できる ない 誉める られる 自信 つく た 好き だ 何気ない やる いる  人 才能 だ  だ 思う
```

* 評価対象データ **[w_nikkei.tsv]**
```
Fri Aug 04 16:31:02 +0000 2017	nikkei	キヤノン電子 4 社 小型衛星 打ち上げる 参入
Fri Aug 04 15:13:02 +0000 2017	nikkei	ポスト安倍 石破 氏 首位 岸田氏 4位
Fri Aug 04 14:12:45 +0000 2017	nikkei	規模 領域 幅広い さ 違う 私たち 多く 共通点 ある マツダ 社長 トヨタ 資本 業務提携 発表 する た 記者会見 一問一答 です
Fri Aug 04 14:07:02 +0000 2017	nikkei	NY 株 上昇 始まる 米 雇用統計 受ける 金融株 買う
Fri Aug 04 13:37:02 +0000 2017	nikkei	内閣支持率 42% 3 ポイント 上昇 本社 世論調査
Fri Aug 04 13:15:49 +0000 2017	nikkei	SingPost chief IS Confide NT of putting company back ON track after months without top management
Fri Aug 04 13:04:02 +0000 2017	nikkei	台風5号 列島 接近 6日 夜 九州 上陸
Fri Aug 04 12:46:02 +0000 2017	nikkei	米 雇用 20 9万人 増 7月 市場 予測 上回る
```

* 評価対象データ **[w_boomin614.tsv]**
```
Sun Jul 23 18:14:21 +0000 2017	boomin614	つぶやき ポジティブ だ  ネガィテブ だ  機械学習 する せる それ 可視 化 する た 結果 です いろいろ 突込み ある 思う 歓迎 する ます なんで 結果 なる た 僕 わかる ます ん それ 機械学習 だ
Sun Jul 23 17:59:27 +0000 2017	boomin614	結局 可視化 こだわる 時間 なる しまう た 明日 どうせ 昼前 出社 予定 だ いい
Sun Jul 23 16:06:59 +0000 2017	boomin614	やっぱり 今日 一 日 使い込む みる た 機械学習 文章 ちょろっと 触る fasttext それ だ いい 途中 ベクトル 演算 ガチ やる たい Neural Network ガチ 機械学習 がっつり tuning しよう 思う た 全然 物足りない
Sun Jul 23 15:56:43 +0000 2017	boomin614	それ 都市伝説 です
Sun Jul 23 15:55:28 +0000 2017	boomin614	気持ち わかる やる みる た 内容 面白い 考える ネタ 的 こっち なる
Sun Jul 23 15:36:21 +0000 2017	boomin614	ちょっと 使い込む みる た Facebook fasttext 使う づらい かゆい  手 届く ない
Sun Jul 23 11:22:25 +0000 2017	boomin614	昨日 お祭り お神輿 担ぐ だ 筋肉痛 だ
Sun Jul 23 09:20:08 +0000 2017	boomin614	原因 分かる た 禁則 文字 入り込む いる た 可視化 こだわる たい それ 結果 見る みる う
```


## 3. 教師データの学習と学習モデル作成
以下が、fasttextで分類を学習させるためのスクリプト[learning.py](learning.py)。

```python
# -*- coding: utf-8 -*-
import fasttext as ft
import argparse

# 実行引数の受け取り
parser = argparse.ArgumentParser(description="学習データを学習し、学習モデルを作る")
parser.add_argument('input', type=str, help="入力ファイルへのPath(必須)")
parser.add_argument('output',type=str, help="出力ファイルへのPath(必須)")
args = parser.parse_args()

# 学習
classifier = ft.supervised(args.input, args.output, dim=400, lr=0.10, epoch=200, thread=6)

# Properties
result = classifier.test(args.input, 2)
print("result.precision", result.precision) # Precision at one
print("result.recall",    result.recall)    # Recall at one
print("result.nexamples", result.nexamples) # Number of test examples
```


以下のように、コマンドラインから、[learning.py](learning.py)を実行する。  
すると、**negaposi.bin** という学習モデルが作成される。


```shell
python learning.py traindata.tsv negaposi
result.precision 0.5
result.recall 1.0
result.nexamples 4608
```

学習データを作るとき、そのモデルに対しての適合率や再現率も、計算している。  


| 観点      | 内容  |
|:----------|:-----------|
| Precision | 適合率のこと。予測を正と判断した中で、答えも正のもの。 |
| Recall    | 再現率のこと。答えが正の中で、予測が正とされたもの。 |


Recallが1.0ということは、ポジティブとラベルしたデータはすべてポジティブに、  
ネガティブとラベルしたデータはすべてネガティブに、分類しているようだ。  
1.0だと、ちょっと過学習しているような気もするのだけど、とりあえずこのまま進める。



## 4. 評価対象データの分類

2.2節で、評価対象データの前処理は、すでに完了させてある。  
その前処理の結果として、 **w_[アカウント名].pkl** のようなファイルが作成されているはずだ。  
このファイルを読み込み、評価結果を出力させていく。

改めて、**w_nikkei.pkl** の中身がどんな内容となっているのか、確認しよう。  
ただ、このpklファイル形式は、pythonのバイナリ保存形式である。  
同じ中身が、plain textで拡張子tsvで出力されているので、これを確認する。

```tsv
2017-08-04 16:31:02	nikkei	キヤノン電子 4 社 小型衛星 打ち上げる 参入
2017-08-04 15:13:02	nikkei	ポスト安倍 石破 氏 首位 岸田氏 4位
2017-08-04 14:12:45	nikkei	規模 領域 幅広い さ 違う 私たち 多く 共通点 ある マツダ 社長 トヨタ 資本 業務提携 発表 する た 記者会見 一問一答 です
2017-08-04 14:07:02	nikkei	NY 株 上昇 始まる 米 雇用統計 受ける 金融株 買う
2017-08-04 13:37:02	nikkei	内閣支持率 42% 3 ポイント 上昇 本社 世論調査
2017-08-04 13:15:49	nikkei	SingPost chief IS Confide NT of putting company back ON track after months without top management
2017-08-04 13:04:02	nikkei	台風5号 列島 接近 6日 夜 九州 上陸
```


このようなデータを元にして、１行ごとに出力されているtweetデータの内容がポジティブなのかネガポジなのかを判定していく。


ここでは、positiveなら+1、negativeなら-1となるようにする。  
具体的には、positiveとnegativeに分類される確率を取得し、negativeの場合は、その確率の値の負を取る。

そのための処理を行うpython script、[judgePositive.py](judgePositive.py)を作ったので、  
この引数に、対象ファイル名と学習データを与えて、結果を得る。

以下のshell scriptで、一気に変換できる。


```shell
echo evaluating tweet data
for item in ${T_ARRAY[@]} ${A_ARRAY[@]} ${NIKKEI[@]}; do
  echo "converting data: "$item
  python judgePositive.py w_${item}.pkl negaposi.bin
done
```

この処理の結果、**result\_w\_[アカウント名].tsv**、**result\_w\_[アカウント名].pkl** といった、  
tsvファイルとpklファイルの2種類が出力される。

それでは、**result_w_nikkei.tsv** の中身を確認してみよう。
```tsv
date	label	posibility	tweet
2017-08-05 01:31:02+09:00	n	-0.998047	キヤノン電子 4 社 小型衛星 打ち上げる 参入
2017-08-05 00:13:02+09:00	n	-0.984375	ポスト安倍 石破 氏 首位 岸田氏 4位
2017-08-04 23:12:45+09:00	p	0.996094	規模 領域 幅広い さ 違う 私たち 多く 共通点 ある マツダ 社長 トヨタ 資本 業務提携 発表 する た 記者会見 一問一答 です
2017-08-04 23:07:02+09:00	n	-0.998047	NY 株 上昇 始まる 米 雇用統計 受ける 金融株 買う
2017-08-04 22:37:02+09:00	p	0.998047	内閣支持率 42% 3 ポイント 上昇 本社 世論調査
2017-08-04 22:15:49+09:00	p	0.962891	SingPost chief IS Confide NT of putting company back ON track after months without top management
2017-08-04 22:04:02+09:00	p	0.992187	台風5号 列島 接近 6日 夜 九州 上陸
2017-08-04 21:46:02+09:00	n	-0.976563	米 雇用 20 9万人 増 7月 市場 予測 上回る
2017-08-04 21:25:02+09:00	p	0.998047	公的年金 運用益 5 1兆円 46 月 株高 追い風
2017-08-04 20:52:02+09:00	n	-0.65625	トヨタ 社長 EV 米 Google Inc. 競う マツダ 会見
2017-08-04 20:45:47+09:00	p	0.832031	高電圧 三菱重工 事務 系 採用 ゼロ 民間 ロケット打ち上げ 失敗 日経 記事 Twitter 読む れる た 10本
```

これだけみると、あまりポジティブとネガティブを判定できていないと、直感的に思える。。。。  
学習データも少ないし、いくら前処理を頑張っても、限界があったのかもしれない。

そもそも、ポジティブ名言の内容で、

    諦めたら、そこで試合終了だよ

というものもあった。ここから、以下のような内容を判定するのは、そもそも無理があるのだろう。

    ＮＹ株、上昇で始まる　米雇用統計受け金融株に買い

これは、株が上がるってことで、誰しもが **「ポジティブ」** ととらえる文章だとう。  
しかし、これがネガティブ判定されてしまっている。  
これが、なぜそうなのか説明できないところが機械学習というか、なんというか。


## 5. 結果の可視化

結果の可視化を行う。  

twitterデータは、時系列情報のデータ。  
そのため、時間とともに、文章から感情の変化を描画することが可能なはず。

また、この結果を複数のアカウントのつぶやきと比較することによって、  
相対的にそのアカウントのつぶやきが、ポジティブなのかネガティブなのかを比較することができる。

[visualizeResult.py](visualizeResult.py)という、可視化のためのscriptも用意した。  


```shell
# 個人的フォロワーなどのアカウント
varray=()
for item in ${T_ARRAY[@]}; do
  varray+=(result_w_$item.pkl)
done
python visualizeResult.py ${varray[@]}

# アニメのセリフなどのbot
varray=()
for item in ${A_ARRAY[@]}; do
  varray+=(result_w_$item.pkl)
done
python visualizeResult.py ${varray[@]}

# 日経関連のアカウント
varray=()
for item in ${NIKKEI[@]}; do
  varray+=(result_w_$item.pkl)
done
python visualizeResult.py ${varray[@]}
```

![result1](Time Series Variation of Emotional Analysis Results from Tweet Data result_w_boomin614.pkl.png )

アカウント名「karen529mm」の発言は、2017年5月ごとにテンションが上がっている。  
何があったのかわからないが、きっとアゲアゲだったのだろう。


![result2](Time Series Variation of Emotional Analysis Results from Tweet Data result_w_matsuoka_shuzo.pkl.png )

松岡修造の安定したポジティブ感wwwwww  

残り2つのアカウントは、エヴァのシンジ君と葛城ミサトのセリフbotなのだが、  
意外にネガティブじゃないのな。



# 5.結果の考察

## 5.1 教師データの分類

学習データの評価で、Recallが1.0だったことに触れた。  
これについても、あえて評価対象データとして可視化してみる。

* ポジティブ名言bot
![教師データ：ポジティブ名言bot](positivebot.png)

* ネガティブ名言bot
![教師データ：ネガティブ名言bot](negativebot.png)

確かにそうなっているようだ。


## 5.2 その他

日経関連アカウントのネガポジ判定を可視化した。  
アカウントごとに発言量が違うので、それもあって期間の長さが違うが、  
同じような記事の見出しのはずなのに、意外にバラける。  


![result3](Time Series Variation of Emotional Analysis Results from Tweet Data result_w_nikkei.pkl.png )


nikkeiWOLとnikkeistyle、nikkeivdata、この3つが、かなりポジティブ寄りの記事らしい。  
ちょっと中身を見てみよう。

* nikkeiWOL：日経ウーマンオンラインのアカウント

```tsv
date	label	posibility	tweet
2017-08-04 22:00:30+09:00	p	0.978516	宝くじ 人生 狂わせる 恐れ ある  合う ない 運試し
2017-08-04 21:00:27+09:00	p	0.998047	自分 何 提供 する ない 他人 モノ 情報 搾取 する まくる 通称 くれる くれる ちゃん 一言 言う たい
2017-08-04 20:00:32+09:00	p	0.998047	多汗症 女性 平均 ワキ 汗 量 汗じみる 危険 行動
2017-08-04 19:00:22+09:00	p	0.998047	皮脂 テカ 毛穴落ち ファンデーション キレイ 直す コツ ある た
2017-08-04 18:15:41+09:00	p	0.994141	グッド!モーニング アワード 2017 結果発表 総合 大賞 ドリンク
2017-08-04 18:00:24+09:00	n	-0.986328	私 汗 臭う 腋臭 体質 分かる チェックリスト
2017-08-04 16:47:31+09:00	p	1.0	暴言 不倫 辞任 騒動 女難 終止符 打つ たい 安倍首相 本気 度 ー 野田聖子 現代 女子 感覚 私たち 閉塞感 救う
2017-08-04 12:05:03+09:00	p	0.978516	相手 心を掴む メール 達人 なる
2017-08-04 12:05:03+09:00	p	0.982422	専業主婦 バリキャリ 堂々 頑張る いる 言う たい
2017-08-04 12:00:13+09:00	n	-0.998047	バリキャリ やめる ます 幹部 候補 中堅 社員 胸の内
2017-08-04 08:09:08+09:00	p	0.998047	夏 持つ たい おすすめ ポーチ 収納 アイテム
2017-08-04 07:53:09+09:00	p	0.724609	寝る 5分 胸 まわり 凝り ほぐす 完全 呼吸法
2017-08-04 07:36:09+09:00	p	0.998047	東京駅 エキナカ 押さえる おく べし 帰省 土産 12 選
2017-08-04 07:20:07+09:00	n	-0.998047	宝くじ 3億円 当選 強 運 つかむ だ 派遣社員 その後
2017-08-04 07:03:09+09:00	n	-0.996094	Chaldee vs Costco 麺 ピザ 菓子 人気 商品 勝負
2017-08-03 23:30:30+09:00	p	0.669922	幸せ アピール 子ども 写真 SNS 投稿 する ワケ
```

うーん、ネガィテブと判定されている文章は、確かにそんな気がする。  
が、ポジティブと判定されているものの中で、なんか違うなと思うものもあるが、  
それは個人で考えや感性も違うだろうから・・・・・(逃



# まとめ

教師データをどのように作るか、がやはり大事。  
日経関連アカウントの場合、記事の内容ごとネガポジ判定して教師データを作ったほうが、  
きっともっと良い結果になっただろう。  
松岡修造や、安西先生のセリフをいくら学習しても、株の上昇をポジティブととらえる学習モデルは  
確かにできなさそうだしな。
# EmotionalAnalisys
