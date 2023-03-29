import os

from bot import Bot
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

if os.environ.get("ENV") == "development":
    print("Loading development environment variables.")
    LINEAPI_ACCESS_TOKEN = os.environ["LINEAPI_ACCESS_TOKEN_DEV"]
    LINEAPI_CHANNEL_SECRET = os.environ["LINEAPI_CHANNEL_SECRET_DEV"]
else:
    LINEAPI_ACCESS_TOKEN = os.environ["LINEAPI_ACCESS_TOKEN"]
    LINEAPI_CHANNEL_SECRET = os.environ["LINEAPI_CHANNEL_SECRET"]


line_bot_api = LineBotApi(LINEAPI_ACCESS_TOKEN)
handler = WebhookHandler(LINEAPI_CHANNEL_SECRET)

bot = Bot()


@app.get("/")
def root():
    return HTMLResponse(content="<h1>Hello World!</h1>", status_code=200)


@app.post("/callback")
async def callback(
    request: Request,
    x_line_signature: str = Header(None),
) -> Response:
    body = (await request.body()).decode("utf-8")
    print(body)

    try:
        handler.handle(body, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=200, detail="Invalid signature")

    return Response(content="OK", status_code=status.HTTP_200_OK)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    event_text = str(event.message.text)
    sender_id = str(event.source.sender_id)
    reply_token = str(event.reply_token)

    # TODO: 初回フォロー時に保存する
    profile = line_bot_api.get_profile(sender_id)
    display_name = str(profile.display_name)

    message = ""
    # if event_text == "start":
    #     message += bot.first_talk()
    # elif event_text == "init":
    #     bot.init_conversation()
    # elif event_text == "base_data":
    #     message = bot.base_data
    # else:
    #     message = bot.talk(event_text)

    # line_bot_api.reply_message(
    #     reply_token,
    #     # TextSendMessage(text=message),
    #     TextSendMessage(text=event_text),
    # )
    line_bot_api.push_message(sender_id, TextSendMessage(text=event_text))
