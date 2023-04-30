import json
import os
import pathlib
import random
from typing import Dict

from utils import save_pickle
from utils.players import ChatBot
from utils.storage import GCSFileManager


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


def main() -> None:
    gcs = GCSFileManager(os.environ["GCS_BUCKET_NAME"])

    user_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
    # user_id = "3704497891"
    user_id = "8560551488"

    system_prompt = gcs.read_file("prompts/start_conversation_v2.txt")
    system_prompt = system_prompt.decode("utf-8")

    is_first = True
    game_settings_filepath = f"game/{user_id}.pkl"
    while True:
        if is_first:
            is_first = False
            if not gcs.exists(game_settings_filepath):
                user_name = input("user_name: ")

                charactor_filepath = random.choice(
                    gcs.list_files("prompts/charactor")
                )
                charactor_id = pathlib.Path(charactor_filepath).name.split(
                    "."
                )[0]

                charactor = get_charactor(gcs, charactor_id)
                print(charactor["summary"] + "\n\n" + "それでは会話を楽しんでください！")
                print("\n", charactor["self_introduction"])

                game_setting = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "charactor_id": charactor["id"],
                }
                save_pickle(f"./data/tmp/{user_id}.pkl", game_setting)
                gcs.update_file(
                    f"./data/tmp/{user_id}.pkl", game_settings_filepath
                )
                system_prompt = system_prompt.replace(
                    "{charactor_settings}", charactor["summary"]
                )
                # TODO: ここでラグが発生し、ユーザがメッセージを送りたいくなってしまう
                print("\n少しの間メッセージが来るのを待ってください...\n")
                bot = ChatBot(
                    charactor_id,
                    system_prompt,
                    f"./data/tmp/memory/{user_id}.pkl",
                )
                response = bot.talk("")
                print(f"{bot.name}:", response, "\n")
                bot.save_memory()
                gcs.update_file(bot.memory_filepath, f"memory/{user_id}.pkl")
        else:
            game_settings = gcs.read_file_as_pickle(game_settings_filepath)
            charactor = get_charactor(gcs, game_settings["charactor_id"])
            system_prompt = system_prompt.replace(
                "{charactor_settings}", charactor["summary"]
            )
            bot = ChatBot(
                game_settings["charactor_id"],
                system_prompt,
                f"./data/tmp/memory/{user_id}.pkl",
            )
            gcs.download_file(f"memory/{user_id}.pkl", bot.memory_filepath)
            bot.load_memory()

            message = input(f"{game_settings['user_name']}: ")
            if message == "exit":
                break

            response = bot.talk(message)
            bot.save_memory()

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
            print(f"{bot.name}:", response, "\n")


if __name__ == "__main__":
    main()
