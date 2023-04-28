import json
import time
from typing import Dict

from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from rich.progress import track


def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f"Spent a total of {cb.total_tokens} tokens")
    return result


def load_txt(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def dump_txt(filepath: str, txt: str) -> None:
    with open(filepath, "w") as f:
        f.write(txt)


def get_charactor_settings(prompt: str) -> Dict[str, str]:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        max_retries=2,
        temperature=0.9,  # type: ignore
    )
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=llm, verbose=False, memory=memory)

    charactor_settings = {}
    charactor_settings["detail"] = conversation.run(input=prompt)
    charactor_settings["summary"] = conversation.run(
        input="キャラクターのことについて300字程度で教えて"
    )
    charactor_settings["self_introduction"] = conversation.run(
        input="キャラクターになりきってフランクな表現で自己紹介をして"
    )
    return charactor_settings


def main() -> None:
    prompt = load_txt("data/prompts/generate_charactor.txt")

    for i in track(range(34, 50)):
        setting = get_charactor_settings(prompt)
        with open(f"data/prompts/charactor/{i:06}.json", "w") as file:
            json.dump(setting, file, indent=2, ensure_ascii=False)
        time.sleep(30)


if __name__ == "__main__":
    main()
