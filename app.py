from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import util
import reptile
import constant
app = Flask(__name__)

configuration = Configuration(access_token=constant.linebot_token)
handler = WebhookHandler(constant.linebot_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
   
    # 將收到的訊息內容，加以分析
    user_needs = util.analyze_text(event.message.text)
    
    # 如果無法分析使用者需求
    if all(element is None for element in user_needs):
        message = [TextMessage(text=constant.user_manual)]
    else:    
        result = reptile.reptile(user_needs)
        if type(result) == list:    
            batch = []
            for content in result:
                analyzed_content = util.analyze_return(content)
                batch.append(TextMessage(text=analyzed_content))
            message = batch[0:5]
        else:
            message = [TextMessage(text=result)]

    if message:
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=message
                    )
                )
        except Exception as e:
            print(f"Failed to send messages: {e}")    


        


import os
if __name__ == "__main__":
    app.run(port=constant.linebot_port)