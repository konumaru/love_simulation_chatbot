import random

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage


def get_basedata() -> str:
    age = random.choices(
        ["現代", "ファンタジー世界", "ダークファンタジー", "SF", "時代劇", "中世", "産業革命期", "スチームパンク"]
    )

    system_prompt = f"""あなたは恋愛ゲームシミュレーターです。

    ###START PROCESS###
    * 世界設定（世界観、時代({age}), 地理, 文化, 文明など）を出力します。
    * ヒロインの名前、プロフィール、性格、口調を出力します。
    * ヒロインの夢、秘密、特技、好きなもの、嫌いなことを出力します。
    * ヒロインの性格パラメーター、会話力, 人懐っこさ、慎重さ、信じやすさ、臆病さ、怒りっぽさ、知性、楽天性をランダムに設定します。

    ###DESIRED FORMAT###
    世界観: $WORLD_RULE,
    ヒロイン名: $NAME,
    プロフィール: $PROFILE,
    性格: $CHARACTER,
    口調: $TONE,
    夢: $DREAM,
    トラウマ: $TRAUMA
    コンプレックス: $INFERIORITY_COMPLEX
    秘密: $SECRET,
    特技: $SKILL,
    好きなもの: $LIKE
    嫌いなもの: $DISLIKE
    ヒロインの性格パラメーター: 会話力:random(10), 人懐っこさ:random(10), 慎重さ:random(10), 信じやすさ:random(10), 臆病さ:random(10), 怒りっぽさ:random(10), 知性:random(10), 楽天性:random(10) 
    """

    messages = [SystemMessage(content=system_prompt), HumanMessage(content="Start")]

    llm = ChatOpenAI(
        model_name="gpt-4",
        top_p=0.5,
        temperature=1,
        frequency_penalty=2,
        max_tokens=2000,
    )  # type: ignore

    # キャラ設定のベースデータを吐き出す。
    res = llm(messages)
    base_data = res.content
    return base_data


def main():
    base_data = get_basedata()
    print(base_data)


if __name__ == "__main__":
    main()
