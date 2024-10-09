from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import *
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os
import requests
import json
import time

app = Flask(__name__)


configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
weath_api = os.getenv('WEATHER_API')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
     
    text = event.message.text    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # Buttons Template
        if text == '文字':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這是文字訊息")]
                )
            )
        elif text == '表情符號':
            emojis = [
                Emoji(index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
                Emoji(index=12, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002")
            ]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='$ LINE 表情符號 $', emojis=emojis)]
                )
            )
        elif text == '貼圖':            
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[StickerMessage(package_id="446", sticker_id="1988")]
                )
            )
        elif text == '圖片':
            url = request.url_root + 'static/Logo.jpg'
            # url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageMessage(original_content_url=url, preview_image_url=url)
                    ]
                )
            )
        elif text == '位置':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        LocationMessage(title='Location', address="Taipei", latitude=25.0475, longitude=121.5173)
                    ]
                )
            )
        elif text == '雷達回波':
            img_url = f'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png?{time.time_ns()}'
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)    
                    ]
                )
            )
        elif text == '地震':
            reply = earth_quake()  # 執行地震查詢函式
            text_message = TextSendMessage(text=reply[0])  # 傳送地震報告內容
            line_bot_api.reply_message(reply_token, text_message)
            if reply[1]:  # 如果有地震圖片，則回傳
                json_data = json.loads(event)
                user_id = json_data['events'][0]['source']['userId']  # 取得使用者 ID
                line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=reply[1], preview_image_url=reply[1]))
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )


# 地震查詢功能，整合中央氣象局地震資料的 API
def earth_quake():
    result = []
    code = weath_api  # 你的天氣 API 授權碼
    try:
        # 小區域地震
        url1 = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
        req1 = requests.get(url1)
        data1 = req1.json()
        eq1 = data1['records']['Earthquake'][0]
        t1 = eq1['EarthquakeInfo']['OriginTime']

        # 顯著有感地震
        url2 = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={code}'
        req2 = requests.get(url2)
        data2 = req2.json()
        eq2 = data2['records']['Earthquake'][0]
        t2 = eq2['EarthquakeInfo']['OriginTime']

        # 使用最新的地震資料
        result = [eq1['ReportContent'], eq1['ReportImageURI']]  # 使用小區域地震
        if t2 > t1:
            result = [eq2['ReportContent'], eq2['ReportImageURI']]  # 如果顯著有感地震時間較近
    except Exception as e:
        print(e)
        result = ['抓取失敗...', '']  # 如果發生錯誤，返回失敗訊息
    return result

def create_rich_menu_1():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=0,
                    y=0,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='雷達回波')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=834,
                    y=0,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='地震')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1663,
                    y=0,
                    width=834,
                    height=843
                ),
                action=MessageAction(text='表情符號')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=0,
                    y=843,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='貼圖') # 圖片
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=834,
                    y=843,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='位置')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1662,
                    y=843,
                    width=834,
                    height=843
                ),
                action=MessageAction(text='F')
            )
        ]

        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(
                width=2500,
                height=1686,
            ),
            selected=True,
            name="圖文選單1",
            chat_bar_text="查看更多資訊",
            areas=areas
        )

        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_create
        ).rich_menu_id

        with open('static/richmenu-1.jpg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )

        line_bot_api.set_default_rich_menu(rich_menu_id)


create_rich_menu_1()

if __name__ == "__main__":
    app.run()
