import json
import os
import pathlib
import pickle
import random
from typing import Dict

import functions_framework
from flask import abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FollowEvent,
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

from utils.players import ChatBot, User
from utils.storage import GCSFileManager

LINEAPI_ACCESS_TOKEN = os.environ["LINEAPI_ACCESS_TOKEN"]
LINEAPI_CHANNEL_SECRET = os.environ["LINEAPI_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINEAPI_ACCESS_TOKEN)
handler = WebhookHandler(LINEAPI_CHANNEL_SECRET)
gcs = GCSFileManager(os.environ["GCS_BUCKET_NAME"])


def random_choice_character() -> Dict[str, str]:
    charactor_filepath = random.choice(gcs.list_files("prompts/charactor"))
    charactor_id = pathlib.Path(charactor_filepath).name.split(".")[0]
    charactor = json.loads(
        gcs.read_file(f"prompts/charactor/{charactor_id}.json").decode("utf-8")
    )
    charactor["id"] = charactor_id
    return charactor


@handler.add(FollowEvent)
def follow_message(event) -> None:
    sender_id = str(event.source.sender_id)
    profile = line_bot_api.get_profile(sender_id)
    display_name = str(profile.display_name)

    charactor = random_choice_character()
    system_prompt = gcs.read_file("prompts/start_conversation_v2.txt")
    system_prompt = system_prompt.replace(
        "{charactor_settings}",
        charactor["summary"],
    )
    player = User(sender_id, display_name, charactor_id=charactor["id"])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=charactor["self_introduction"]),
    )

    message = f"これからよろしくお願いします！{player.user_name}さん！"
    line_bot_api.push_message(
        sender_id,
        TextSendMessage(text=message),
    )

    # Save user and chatbot data in local.
    bot = ChatBot(
        charactor["id"],
        system_prompt,
        f"{charactor['id']}/memory/{player.user_id}.pkl",
    )
    bot.save_memory()
    with open(f"user_{player.user_id}.pkl", "wb") as f:
        pickle.dump(player, f)

    # Upload to user and chatbot data to GCS.
    gcs.update_file(
        f"{charactor['id']}/memory/{player.user_id}.pkl",
        f"{charactor['id']}/memory/{player.user_id}.pkl",
    )
    gcs.update_file(f"user_{player.user_id}.pkl", f"user_{player.user_id}.pkl")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event) -> None:
    sender_id = str(event.source.sender_id)
    player = gcs.read_file(f"user_{sender_id}.pkl")
    charactor_id = player.conversation_charactor_id

    system_prompt = gcs.read_file("prompts/start_conversation_v2.txt")
    charactor = json.loads(
        gcs.read_file(f"prompts/charactor/{charactor_id}.json").decode("utf-8")
    )
    system_prompt = system_prompt.replace(
        "{charactor_settings}",
        charactor["summary"],
    )

    bot = ChatBot(
        charactor_id,
        system_prompt,
        f"./data/{charactor_id}/memory/{player.user_id}.pkl",
    )
    event_text = str(event.message.text)
    response = bot.talk(event_text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response),
    )
    bot.save_memory()


@functions_framework.http
def main(request):
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"
