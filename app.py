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

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

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
            url = request.url_root + '/static/Logo.jpg'
            url = url.replace("http", "https")
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
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )




if __name__ == "__main__":
    app.run()
