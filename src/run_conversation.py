import json
import os
import pathlib
import random

from utils.players import ChatBot, User
from utils.storage import GCSFileManager


def load_txt(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def main() -> None:
    gcs = GCSFileManager(os.environ["GCS_BUCKET_NAME"])
    charactor_filepath = random.choice(gcs.list_files("prompts/charactor"))
    charactor_id = pathlib.Path(charactor_filepath).name.split(".")[0]
    charactor = json.loads(
        gcs.read_file(f"prompts/charactor/{charactor_id}.json").decode("utf-8")
    )
    # charactor_id = "000005"

    system_prompt = load_txt("data/prompts/start_conversation_v2.txt")
    system_prompt = system_prompt.replace(
        "{charactor_settings}", charactor["summary"]
    )
    user_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
    # user_id = "3704497891"
    user_name = input("user_name: ")
    player = User(user_id, user_name)

    bot = ChatBot(
        charactor_id,
        system_prompt,
        f"./data/{charactor_id}/memory/{user_id}.pkl",
    )

    is_first = True
    while True:
        if is_first:
            print(charactor["self_introduction"])
            message = system_prompt
            is_first = False
        else:
            message = input(f"{player.user_name}: ")
        response = bot.talk(message)
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

        if message == "exit":
            break

        print(f"{bot.name}:", response, "\n")
        bot.save_memory()


if __name__ == "__main__":
    main()
