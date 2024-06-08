# trading_system

## Overview

auカブコム証券さんが提供しているAPIを利用したシステムトレーディングです。
有識者の方のブログ等を参考に作成しました。感謝しております。

利用にはカブコム証券口座及び信用取引口座の開設が必要です。


## Requirement

* Windows 10,11
* Python3
* pandas
* yfinance
* ta-lib
* logging

# Installation

```bash
pip install pandas yfinance ta-lib  logging
```

# Usage
実行前にkabuステーションアプリにログイン状態である必要があります。

```bash
git clone https://github.com/ys4614/trading_system/
cd python
python main.py
```

# Note

ロジックをそのまま使用しても利益は得られないので、チューニングは必須です!(^^)!
自動トレードで楽に稼ごうとしたが、失敗した良い例だと思っています。

# Author

[twitter](https://x.com/pikarihikari78)

# License

This is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).

