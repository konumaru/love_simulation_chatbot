import os
from datetime import timedelta

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from src.bot import Bot

app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


bot = Bot()


@app.route("/")
def test():
    return "<h1>It Works!</h1>"


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
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    event_text = str(event.message.text)

    if event_text == "start":
        bot.init_conversation()
        message = bot.first_talk()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message),
        )
    else:
        first_chat = bot.talk(event_text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=first_chat),
        )

    # NOTE: Replay the same message.
    # line_bot_api.reply_message(
    #     event.reply_token, TextSendMessage(text=event.message.text)
    # )


if __name__ == "__main__":
    #    app.run()
    app.run(host="0.0.0.0", port=5000)
