# 🃏 Python-Blackjack
PythonのSocketを用いたBlackjackゲーム

## 🍙 メンバー紹介
- T5-10 温 翔毅
- T5-10 酒井 脩作
- T5-23 下山 歩

## ❓ 使い方
1. このリポジトリを Clone する

```
git clone https://github.com/Shimoyama0711/Python-Blackjack.git
```

2. 最初に `blackjack_server.py` を引数なしで実行する
```
$ python blackjack_server.py
```

3. 次に `Server` を実行しているコンピュータのIPアドレスを引数1に指定して `blackjack_client.py` を実行する
```
$ python blackjack_client.py 127.0.0.1
```

4. `[H]` で Hit、`[S]` でStand します

5. 対戦が終わったら **Client** 側の通信は自動的に切断されます。
6. **Server** 側の通信は Ctrl+C などで終了してください

## 🤔 これはなに？ TL;DR
コンピューターネットワークII の授業の一貫で製作したBlackjackゲームです。

## ⚖️ ルール
1. 最初に **Client** の番が始まります。
2. Hitを繰り返し、手札の合計が **21** に近づくように調整します。
3. 札は、`2` ～ `10` はそのまま、`J`、`Q`、`K` は `10` として扱い、`A` は `1` か `11` かを選べます。
4. **Client** の番が終わったら **Server** の番になります。
5. 手札の合計が **22** 以上になってしまったら、**Bust** となり、負けます。
