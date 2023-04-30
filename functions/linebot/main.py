import json
import os
import pathlib
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

from utils import save_pickle
from utils.players import ChatBot
from utils.storage import GCSFileManager

LINEAPI_ACCESS_TOKEN = os.environ["LINEAPI_ACCESS_TOKEN"]
LINEAPI_CHANNEL_SECRET = os.environ["LINEAPI_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINEAPI_ACCESS_TOKEN)
handler = WebhookHandler(LINEAPI_CHANNEL_SECRET)
gcs = GCSFileManager(os.environ["GCS_BUCKET_NAME"])


def random_choice_character(gcs: GCSFileManager) -> Dict[str, str]:
    charactor_filepath = random.choice(gcs.list_files("prompts/charactor"))
    charactor_id = pathlib.Path(charactor_filepath).name.split(".")[0]
    charactor = json.loads(
        gcs.read_file(f"prompts/charactor/{charactor_id}.json").decode("utf-8")
    )
    charactor["id"] = charactor_id
    return charactor


def get_charactor(gcs: GCSFileManager, charactor_id: str) -> Dict[str, str]:
    charactor = json.loads(
        gcs.read_file(f"prompts/charactor/{charactor_id}.json").decode("utf-8")
    )
    charactor["id"] = charactor_id
    return charactor


def get_system_prompt(gcs: GCSFileManager) -> str:
    system_prompt = gcs.read_file("prompts/start_conversation_v2.txt")
    system_prompt = system_prompt.decode("utf-8")
    return system_prompt


def cleanup_bot_response(response: str) -> str:
    remove_words = [
        "Chatbot",
        "ChatBot",
        "chatbot",
        "chatBot",
        ":",
        "[",
        "]",
    ]
    for w in remove_words:
        response = response.replace(w, "")
    return response


@handler.add(FollowEvent)
def follow_message(event) -> None:
    sender_id = str(event.source.sender_id)
    profile = line_bot_api.get_profile(sender_id)
    display_name = str(profile.display_name)

    # Send welcome message.
    charactor = random_choice_character(gcs)
    message = charactor["summary"] + "\n\n" + "それでは会話を楽しんでください！"
    line_bot_api.push_message(
        sender_id,
        TextSendMessage(text=message),
    )
    line_bot_api.push_message(
        sender_id,
        TextSendMessage(text=charactor["self_introduction"]),
    )
    # Define and save game settings.
    game_settings_filepath = f"game_settings_{sender_id}.pkl"
    game_settings = {
        "user_id": sender_id,
        "user_name": display_name,
        "charactor_id": charactor["id"],
    }
    save_pickle(game_settings_filepath, game_settings)
    gcs.update_file(game_settings_filepath, f"game_settings/{sender_id}.pkl")

    # Send first message from chatbot.
    system_prompt = get_system_prompt(gcs)
    system_prompt = system_prompt.replace(
        "{charactor_settings}",
        charactor["summary"],
    )
    bot = ChatBot(
        game_settings["charactor_id"],
        system_prompt,
        f"memory_{sender_id}.pkl",
    )
    response = bot.talk("")
    line_bot_api.push_message(
        sender_id,
        TextSendMessage(text=response),
    )
    bot.save_memory()
    gcs.update_file(f"memory_{sender_id}.pkl", f"memory/{sender_id}.pkl")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event) -> None:
    sender_id = str(event.source.sender_id)

    game_settings = gcs.read_file_as_pickle(f"game_settings/{sender_id}.pkl")
    charactor = get_charactor(gcs, game_settings["charactor_id"])

    system_prompt = get_system_prompt(gcs)
    system_prompt = system_prompt.replace(
        "{charactor_settings}",
        charactor["summary"],
    )

    bot = ChatBot(
        game_settings["charactor_id"],
        system_prompt,
        f"memory_{sender_id}.pkl",
    )
    gcs.download_file(f"memory/{sender_id}.pkl", f"memory_{sender_id}.pkl")
    bot.load_memory()

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
