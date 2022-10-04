# 台股機器人

## 安裝、設定

### 安裝Python

>建議使用Python3.7，並且將python安裝路徑加入到環境變數的PATH中

pip下指令:

    pip install -r requirements.txt

### 安裝MySQL

Windows 載點 : [MySQL Windows Installer Donwload](https://dev.mysql.com/downloads/installer/)

將 [sql](/database/linebot_stock.sql) 匯入至資料庫中 (資料庫名為linebot_stock)

### Line設定

你需要:

1. Channel ID
2. Channel secret
3. Webhook網址 -> https://你的域名/callback

>此範例使用 ngrok 取得 https 網址

### 程式設定

手動複製 config.py.example，修改參數完成後，將檔名改為 config.py

----------------

## 使用

開啟命令提示字元後，進入到 asialinebot_stock 資料夾

下指令:

    py main.py

或是:

    python3 main.py
