import os

from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# generate instance
app = Flask(__name__)

# get environmental value from heroku
ACCESS_TOKEN = "07ctImR0LTjG2xo58kaSPQI5DofbBit/EcEbKoWKrHjqfnQmmt9dNqkHJAiw8wknHBPJvPq3jrZkV6iLeSiSmmHaBAacGZ/rQVToaGuD0xzTimahTrDQWPkF4Z/eE0Y/JgJAsMmygpSL9AnOJAhf1gdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "fc1992044e78ee2c8844c78f64d9e53a"
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# endpoint
@app.route("/")
def test():
    return "<h1>It Works!</h1>"


# endpoint from linebot
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
    return "OK"


# handle message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )


if __name__ == "__main__":
    app.run()
