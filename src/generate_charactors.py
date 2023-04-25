from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


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
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=llm, verbose=False, memory=memory)

    _ = conversation.run(input=prompt)
    result = conversation.run(input="日本語で300文字程度に要約して")
    return result


def main():
    prompt = load_txt("data/prompts/generate_charactor.txt")

    for i in range(50):
        setting = get_charactor_settings(prompt)
        dump_txt(f"data/prompts/charactor/{i:06}.txt", setting)


if __name__ == "__main__":
    main()
