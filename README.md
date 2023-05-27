# 台股小百科

使用LINE Messaging-api 建立可查詢台股相關資訊的LINE機器人。

* 下載
* 安裝
* 設定
* 設定完成範例
* 使用範例

-----

## 1. 下載
[Github連結](https://github.com/TaiwanAsia/asiatwlinebot_stock)

![下載](https://i.imgur.com/sSIM0aY.png)

下載後解壓縮至你要的目錄，我的是D:\git\，解壓縮後會是G:\git\asiatwlinebot_stock\

-----

## 2. 安裝

### 安裝 - Python

>建議使用Python3.7↑，並且將python安裝路徑加入到環境變數的PATH中

開啟命令提示字元後，pip or pip3 下指令:
`pip install -r requirements.txt` 或 `pip3 install -r requirements.txt`

另外安裝pymsql
`pip install pymysql` 或 `pip3 install pymysql`

### 安裝 - MySQL

Windows 載點 : [MySQL Windows Installer Donwload](https://dev.mysql.com/downloads/installer/)

**[安裝教學](https://ithelp.ithome.com.tw/articles/10259766)** - 記得設定的密碼

將 [sql](/database/linebot_stock.sql) 匯入至資料庫

-----

## 3. 設定

### 設定 - 程式

手動複製 config.py.example，修改參數完成後(可看[設定 - LINE])，將檔名改為 config.py

### 設定 - 架站

開啟命令提示字元後，進入到 asialinebot_stock 資料夾。如非臨時架站，則從Step 5開始

1. 臨時架站： 註冊並下載ngrok [官網](https://dashboard.ngrok.com/get-started/setup "ngrok")，將下載的 ngrok.exe 放入該 asiatwlinebot_stock 資料夾內

2. 上一步註冊登入ngrok後，去Your Authtoken找到自己的token並複製

3. 打開命令提示字元(進入到 asialinebot_stock 資料夾)，輸入
`ngrok authtoken [你在第2步複製的token]`

4. 運行ngrok
`ngrok http 8888`

5. 下指令:
`py app.py` 或 `python3 app.py`

### 設定 - LINE

你需要先到 LINE Developers 新建 Providers、Channels：

1. 記下<font color=#0000FF>Channel ID</font>，填入上述 [設定 - 程式] 所說config.py內
2. 記下<font color=#0000FF>Channel secret</font>，填入上述 [設定 - 程式] 所說config.py內
3. <font color=red>Webhook URL</font> 填入 -> <https://你的域名/callback>。
你的域名就是架站步驟4，運行ngrok後顯示出的網址，記得選https開頭的那個
![選第二個網址](https://i.imgur.com/bA43inC.png)

4. 如果遇到這行錯誤 ![cryptography](https://i.imgur.com/3BT0Wwd.png)
如同安裝步驟，開啟命令提示字元，執行`pip install cryptography`

-----

## 4. 設定完成範例
![config.py](https://i.imgur.com/jcjChit.png)
圖中1處為下載、安裝mysql時設定的密碼
## 5. 使用範例

![輸入中文](https://i.imgur.com/YIy3RKl.png)
![輸入統一編號](https://i.imgur.com/jV1dQ3T.png)