from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage


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


def get_charactor_settings(prompt: str) -> str:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        max_retries=2,
        temperature=0.9,  # type: ignore
    )
    conversation = ConversationChain(
        llm=llm,
        verbose=False,
        memory=ConversationBufferMemory(),
    )

    result = conversation.run(input=prompt)
    result = conversation.run(
        input="Please summarize in 300 words the details of the character and translate into Japanese."
    )
    return result


def main():
    prompt = load_txt("data/prompts/generate_charactor.txt")

    setting = get_charactor_settings(prompt)
    print(setting)

    dump_txt("data/prompts/charactor/A.txt", setting)


if __name__ == "__main__":
    main()
