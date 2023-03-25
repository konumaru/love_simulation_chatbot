from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(
    "07ctImR0LTjG2xo58kaSPQI5DofbBit/EcEbKoWKrHjqfnQmmt9dNqkHJAiw8wknHBPJvPq3jrZkV6iLeSiSmmHaBAacGZ/rQVToaGuD0xzTimahTrDQWPkF4Z/eE0Y/JgJAsMmygpSL9AnOJAhf1gdB04t89/1O/w1cDnyilFU="
)
handler = WebhookHandler("fc1992044e78ee2c8844c78f64d9e53a")


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
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )


if __name__ == "__main__":
    app.run()
