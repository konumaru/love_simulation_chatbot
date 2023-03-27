import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fastapi import FastAPI, HTTPException, Request, Header

from bot import Bot

app = FastAPI()

line_bot_api = LineBotApi(os.environ["LINEAPI_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINEAPI_CHANNEL_SECRET"])

bot = Bot()


@app.get("/")
def root():
    return "Hello World!"


@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = (await request.body()).decode("utf-8")

    try:
        handler.handle(body, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    event_text = str(event.message.text)

    message = ""
    if event_text == "start":
        message += bot.first_talk()
    elif event_text == "init":
        bot.init_conversation()
    elif event_text == "base_data":
        message = bot.base_data
    else:
        message = bot.talk(event_text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message),
    )
