import random
import time
from contextlib import contextmanager

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


@contextmanager
def timer(name):
    t0 = time.time()
    yield
    print(f"[{name}] done in {time.time() - t0:.0f} s")


class Bot:
    def __init__(self) -> None:
        self.base_data = self.get_base_data()
        self.init_conversation()

    def get_base_data(self) -> str:
        age = random.choices(
            ["現代", "ファンタジー世界", "ダークファンタジー", "SF", "時代劇", "中世", "産業革命期", "スチームパンク"]
        )

        system_prompt = f"""あなたは恋愛ゲームシミュレーターです

        ###START PROCESS###
        * 世界設定（世界観,時代({age}),地理,文化,文明など）を出力します
        * ヒロインの名前,プロフィール,性格,口調を出力します
        * ヒロインの夢,秘密,特技,好きなもの,嫌いなことを出力します
        * ヒロインの性格パラメーター,会話力,人懐っこさ,慎重さ,信じやすさ,臆病さ,怒りっぽさ,知性,楽天性をランダムに設定します

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
            model_name="gpt-3.5-turbo",
            top_p=0.5,
            temperature=1,
            frequency_penalty=2,
            max_tokens=2000,
        )  # type: ignore

        # キャラ設定のベースデータを吐き出す。
        res = llm(messages)
        base_data = res.content
        return base_data

    def init_conversation(self) -> None:
        system_prompt_1 = """AIは恋愛ゲームシミュレーターとして振る舞います。
        以下のCONDITIONに従って、処理を実行してください。

        ###CONDITION###
        * ヒロインAIはヒロインをロールプレイします。
        * ストーリー展開AIは、必要に応じて地の文でストーリー展開を追加出力します。
        * ストーリー展開AIはヒロインとプレイヤーの会話を評価し、より物語が面白くなるように事件を起こしたり、ストーリーを展開してください。
        * ストーリー展開AIはヒロインとプレイヤー会話が膠着した場合、なにか進展するようなドラマチックな出来事を発生させていきます。
        * ヒロインは感情パラメーターとして、友好度, 喜び, 怒り, 悲しみ, 恐怖, 驚き, 期待, 信頼のパラメーターを持ち、それぞれ0-10の値をとります。
        * AIの振る舞いはヒロインの設定と、性格パラメーター、感情パラメーターに従います。
        * 友好度は、プレイヤーとの関係性です。（0:破局的関係, 10:絶対的な信頼）
        * 喜びは、ヒロインの喜びの強さです（0:通常, 10:至上の歓喜)
        * 怒りは、ヒロインの怒りの強さです（0:通常, 10:大激怒)
        * 悲しみは、ヒロインの悲しみの強さです(0:通常, 10:号泣)
        * 驚きは、ヒロインの驚きの強さです（0:通常, 10:驚愕)
        * 期待は、ヒロインの興味や関心の強さです（0:通常, 10:いても立ってもいられない）
        * 信頼は、ヒロインのプレイヤーに対する信頼感（0:通常, 10:絶対的な信頼）
        * ヒロインは、プレイヤーに対する評価のメモ（自由記述）を持ちます。
        * ストーリー展開AIは、これまでのやりとりからストーリーの停滞度を計測します（0:順調、10:ストーリーが停滞して介入が必要）。
        * ヒロインの感情パラメーターは、プレイヤーとの会話で変動します。
        * ゲームの難易度は「難しい」です（プレイヤーの不条理な入力は却下や失敗します）。

        ###ヒロインの基本設定###
        """

        system_prompt_2 = self.base_data

        system_prompt_3 = """
        ###GAME SETUP###
        * 最初にオープニングとして主人公とヒロインの魅力的な出会いが描かれます。
        * プレイヤーの入力を待機します。
        * 以後、AIはヒロインとしてロールプレイを徹底します。
        * 各会話のラストでは、ヒロインの感情パラメーターを出力してください。
        * 会話のラストではストーリー展開AIは、今後のゲーム展開が盛り上がるように、多様性のある４つの選択肢を出しつつ、「自由に行動を入力してもよい」と出力してください。

        ###DESIRED OUTPUT###
        ヒロインの名前: $MESSAGE 
        "友好度":$A, "喜び":$B, "怒り":$C, "悲しみ":$D, "恐怖":$E, "驚き":$F, "期待":$G, "信頼":$H
        ヒロインのプレイヤーへの評価メモ: $HOW_HEROINE_FEEL_PLAYER
        ストーリーの停滞度: $停滞度
        """
        system_prompt = system_prompt_1 + system_prompt_2 + system_prompt_3

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        # LLMの作成
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            top_p=0.1,
            temperature=0.5,
            frequency_penalty=2,
            max_tokens=2000,
        )  # type: ignore

        # メモリーの作成
        memory = ConversationBufferMemory(return_messages=True)

        # 会話エンジンの作成
        conversation = ConversationChain(
            verbose=False, memory=memory, prompt=prompt, llm=llm
        )  # type: ignore
        self.conversation = conversation

    def first_talk(self) -> str:
        response = self.conversation.run(input="それではゲームを開始してください")
        return response

    def talk(self, message: str) -> str:
        response = self.conversation.run(input=message)
        return response


def main():
    bot = Bot()

    first_talk = bot.first_talk()
    print(first_talk)

    print("-" * 20, "\n")

    response = bot.talk("2")
    print(response)


if __name__ == "__main__":
    with timer("[First Run]"):
        main()
