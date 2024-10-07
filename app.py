from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
import linebot.v3.messaging *
import linebot.v3.webhooks *
import os
#Azure CLU
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
# clu_endpoint = os.getenv("ENDPOINT")
# clu_key = os.getenv("API_KEY")
# project_name = os.getenv("PROJECT_NAME")
# deployment_name = os.getenv("DEPLOYMENT_NAME")  

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

        # Confirm Template
        if text == 'Confirm':
            confirm_template = ConfirmTemplate(
                text='今天學程式了嗎?',
                actions=[
                    MessageAction(label='是', text='是!'),
                    MessageAction(label='否', text='否!')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        # Buttons Template
        elif text == 'Buttons':
            url = request.url_root + '/static/Logo.jpg'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='示範',
                text='詳細說明',
                actions=[
                    URIAction(label='連結', uri='https://www.facebook.com/NTUEBIGDATAEDU'),
                    PostbackAction(label='回傳值', data='ping', displayText='傳了'),
                    MessageAction(label='傳"哈囉"', text='哈囉'),
                    DatetimePickerAction(label="選擇時間", data="時間", mode="datetime")
                ]
            )
            template_message = TemplateMessage(
                alt_text="This is a buttons template",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        # Carousel Template
        elif text == 'Carousel':
            url = request.url_root + '/static/Logo.jpg'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            carousel_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=url,
                        title='第一項',
                        text='這是第一項的描述',
                        actions=[
                            URIAction(
                                label='按我前往 Google',
                                uri='https://www.google.com'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=url,
                        title='第二項',
                        text='這是第二項的描述',
                        actions=[
                            URIAction(
                                label='按我前往 Yahoo',
                                uri='https://www.yahoo.com'
                            )
                        ]
                    )
                ]
            )

            carousel_message = TemplateMessage(
                alt_text='這是 Carousel Template',
                template=carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages =[carousel_message]
                )
            )
                
        elif text == '文字':
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
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )




if __name__ == "__main__":
    app.run()
