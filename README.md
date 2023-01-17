# 台股小百科

使用LINE Messaging-api 建立可查詢台股相關資訊的LINE機器人。
>此機器人使用 ngrok 取得 https 網址

## 安裝、設定

### 安裝Python

>建議使用Python3.7，並且將python安裝路徑加入到環境變數的PATH中

pip or pip3 下指令:
`pip install -r requirements.txt`

### 安裝MySQL

Windows 載點 : [MySQL Windows Installer Donwload](https://dev.mysql.com/downloads/installer/)

將 [sql](/database/linebot_stock.sql) 匯入至資料庫

## 如何設定

### 設定 - 程式

手動複製 config.py.example，修改參數完成後，將檔名改為 config.py

### 設定 - 命令提示字元

開啟命令提示字元後，進入到 asialinebot_stock 資料夾。

1. 運行ngrok
`ngrok http 8888`

2. 下指令:
`py main.py 或 python3 main.py`

### 設定 - LINE

你需要先到 LINE Developers 新建 Providers、Channels：

1. 記下<font color=#0000FF>Channel ID</font>，填入上述所說config.py內
2. 記下<font color=#0000FF>Channel secret</font>，填入上述所說config.py內
3. <font color=red>Webhook URL</font> 填入 -> <https://你的域名/callback> (你的域名就是上個步驟運行ngrok後，顯示出的網址)

----------------

## 範例

![輸入中文](https://i.imgur.com/YIy3RKl.png)
![輸入統一編號](https://i.imgur.com/jV1dQ3T.png)