import os

import uvicorn
from bot import ChatBot
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FollowEvent,
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

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


@handler.add(FollowEvent)
def follow_message(event) -> None:
    sender_id = str(event.source.sender_id)
    profile = line_bot_api.get_profile(sender_id)
    display_name = str(profile.display_name)

    bot = ChatBot(sender_id, display_name, initialize=True)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bot.backgroud),
    )

    first_message = bot.talk("")
    line_bot_api.push_message(
        sender_id,
        TextSendMessage(text=first_message),
    )
    bot.save_memory()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event) -> None:
    sender_id = str(event.source.sender_id)
    profile = line_bot_api.get_profile(sender_id)
    display_name = str(profile.display_name)
    event_text = str(event.message.text)

    bot = ChatBot(sender_id, display_name)
    bot.load_memory()
    message = bot.talk(event_text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message),
    )
    bot.save_memory()


def main() -> None:
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ["PORT"]),
        reload=True,
    )


if __name__ == "__main__":
    main()
