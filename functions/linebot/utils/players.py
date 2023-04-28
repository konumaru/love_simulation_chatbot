import os
import pickle

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate


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
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["history", "input"],
        )
        self.conversation = self._init_conversation()

        self.name = "ChatBot"

    def _init_conversation(self) -> ConversationChain:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            top_p=0.5,  # type: ignore
            temperature=0.7,  # type: ignore
            frequency_penalty=2,  # type: ignore
            max_tokens=2000,
        )
        conversation = ConversationChain(
            llm=llm, memory=self.memory, prompt=self.prompt, verbose=False
        )
        return conversation

    def talk(self, message: str) -> str:
        response = self.conversation.run(input=message)
        return response

    def load_memory(self) -> ConversationSummaryBufferMemory:
        if os.path.exists(self.memory_filepath):
            with open(self.memory_filepath, "rb") as f:
                return pickle.load(f)
        else:
            return ConversationSummaryBufferMemory(
                llm=OpenAI(), max_token_limit=100  # type: ignore
            )

    def save_memory(self) -> None:
        if os.path.exists(self.memory_filepath):
            saved_dir = os.path.dirname(self.memory_filepath)
            os.makedirs(saved_dir, exist_ok=True)

        with open(self.__module__, "wb") as f:
            pickle.dump(self.memory, f)


class User:
    def __init__(
        self, user_id: str, user_name: str, charactor_id: str
    ) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.conversation_charactor_id = charactor_id
