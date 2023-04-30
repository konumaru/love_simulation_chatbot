import os
import pickle

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage


class ChatBot:
    def __init__(
        self,
        charactor_id: str,
        prompt_template: str,
        memory_filepath: str,
    ) -> None:
        self.window_size = 10
        self.charactor_id = charactor_id
        self.memory_filepath = memory_filepath
        self.memory = self.load_memory()
        self.prompt_template = prompt_template
        self.conversation = self._init_conversation()

        self.name = "ChatBot"

    def _init_conversation(self) -> ConversationChain:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    self.prompt_template
                ),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            top_p=0.5,  # type: ignore
            temperature=0.3,  # type: ignore
            frequency_penalty=2,  # type: ignore
            max_tokens=2500,
        )
        conversation = ConversationChain(
            llm=llm, memory=self.memory, prompt=prompt, verbose=False
        )
        return conversation

    def talk(self, message: str) -> str:
        response = self.conversation.predict(input=message)
        return response

    def load_memory(self) -> ConversationBufferWindowMemory:
        if os.path.exists(self.memory_filepath):
            with open(self.memory_filepath, "rb") as f:
                return pickle.load(f)
        else:
            return ConversationBufferWindowMemory(
                k=self.window_size, return_messages=True
            )

    def save_memory(self) -> None:
        if os.path.exists(self.memory_filepath):
            saved_dir = os.path.dirname(self.memory_filepath)
            os.makedirs(saved_dir, exist_ok=True)

        with open(self.memory_filepath, "wb") as f:
            pickle.dump(self.memory, f)
