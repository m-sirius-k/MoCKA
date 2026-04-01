# MoCKA Router API 仕様書

## 概要
interface/router.py はMoCKAの単一入口です。

## 関数一覧

### save
python interface/router.py save "タイトル" "内容"

### share
python interface/router.py share "内容"

### collaborate
python interface/router.py collaborate "問い"

## 動的制御
- <1.0 full_orchestra
- <2.0 share_only
- <3.0 save_only
- >=3.0 audit_mode

## 記録
error_rate / router_mode / response_time
