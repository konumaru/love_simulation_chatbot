import pathlib
import pickle
import random
import re
import time
from contextlib import contextmanager
from typing import Any, List

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage


class ChatBot:
    def __init__(
        self,
        partner_user_id: str,
        partner_user_name: str,
        initialize: bool = False,
    ) -> None:
        self.partner_user_id = partner_user_id
        self.partner_user_name = partner_user_name
        self.gen_charactor_filepath = "./prompts/generate_charactor.txt"
        self.gen_first_message_filepath = "./prompts/start_conversation.txt"

        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            top_p=0.5,  # type: ignore
            temperature=1,  # type: ignore
            frequency_penalty=2,  # type: ignore
            max_tokens=2000,
        )

        self.charactor_name = ""
        self.save_dir = pathlib.Path(f"./data/{partner_user_id}")
        if initialize or not self.save_dir.exists():
            self.save_dir.mkdir(exist_ok=True)

            while len(self.charactor_name) == 0:
                self.backgroud = self.gen_background()
                self.charactor_name = self._get_charactor_name(self.backgroud)

            self._save_txt(str(self.save_dir / "background"), self.backgroud)
            self._save_txt(
                str(self.save_dir / "charactor_name"),
                self.charactor_name,
            )

            self.memory = ConversationBufferWindowMemory(
                k=20, return_messages=True
            )
            self.conversation = self._get_conversation(self.memory)
        else:
            self.charactor_name = self._load_txt(
                str(self.save_dir / "charactor_name")
            )
            self.memory = self.load_pickle(str(self.save_dir / "memory.pkl"))
            self.conversation = self._get_conversation(self.memory)

    def load_pickle(self, filepath: str) -> Any:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        return data

    def save_pickle(self, filepath: str, data: Any) -> None:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_txt(self, filepath) -> str:
        with open(filepath, "r") as file:
            txt = file.read()
        return txt

    def _save_txt(self, filepath, txt) -> str:
        with open(filepath, "w") as file:
            file.write(txt)
        return "saved text"

    def gen_background(self) -> str:
        world = self._get_age()
        prompt = self._load_txt(self.gen_charactor_filepath)
        prompt = prompt.format(age=world)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content="Start"),
        ]
        res = self.llm(messages)
        content = res.content
        return content

    def _get_age(self) -> List[str]:
        age = random.choices(
            [
                "現代",
                "ファンタジー世界",
                "ダークファンタジー",
                "SF",
                "時代劇",
                "中世",
                "産業革命期",
                "スチームパンク",
            ]
        )
        return age

    def _get_charactor_name(self, greeting_message: str) -> str:
        match = re.search(
            r"\[ヒロイン名\]=: (.+)",
            greeting_message,
        )
        charactor_name = ""
        if match:
            charactor_name = match.group(1)
            charactor_name = re.sub(r"\s", "", charactor_name)  # スペースも除去する
        return charactor_name

    def _get_conversation(
        self, memory: ConversationBufferWindowMemory
    ) -> ConversationChain:
        system_prompt = self._load_txt(self.gen_first_message_filepath)
        system_prompt = system_prompt.format(
            charactor_name=self.charactor_name,
            partner_user_name=self.partner_user_name,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )
        conversation = ConversationChain(
            verbose=False, memory=memory, prompt=prompt, llm=self.llm
        )  # type: ignore
        return conversation

    def talk(self, message: str) -> str:
        response = self.conversation.run(input=message)
        return response

    def load_memory(self) -> None:
        self.memory = self.load_pickle(str(self.save_dir / "memory.pkl"))

    def save_memory(self) -> None:
        self.save_pickle(str(self.save_dir / "memory.pkl"), self.memory)


def main() -> None:
    bot = ChatBot("sample_user_id", "user_name", True)

    print(bot.backgroud)
    print("-" * 20, "\n")

    for i in range(4):
        if i == 0:
            response = bot.talk("")
        else:
            bot.load_memory()
            response = bot.talk(str(i))

        print(response)
        print("-" * 20, "\n")

        bot.save_memory()


if __name__ == "__main__":
    with timer("[First Run]"):
        main()
