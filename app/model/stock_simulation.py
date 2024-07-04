import asyncio

import pandas as pd
import random
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.prompt.prompt_version import get_system_prompt, PromptVersion
from app.utils.json_parser import parse


# 주식 가격 변동 시뮬레이션 함수
def simulate_stock_changes(stocks, news_effects, day):
    for industry, price in stocks.items():
        daily_change = random.randint(-20, 20)
        stocks[industry] += daily_change

        # 뉴스 효과 적용
        if day == 15 :
            stocks[industry] += news_effects["news_effects"][industry]


    return stocks


async def main():
    # 예시 뉴스 효과 (양수는 호재, 음수는 악재)
    # load env
    load_dotenv()

    ai_client = get_platform_client(LLMModel.OPENAI_GPT4o)
    #
    # 프롬프트
    system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_04)
    #
    # # 크롤링한 기사
    request_text = """(서울=연합뉴스) 권지현 기자 = "하다못해 감기에만 걸려도 그게 맞는지 아닌지, 어떤 약을 어떻게 먹어야 하는지 몰라서 병원을 가는 게 환자잖아요. 그런데 의료사고의 진실을 어떻게 밝혀내나요." 강남의 한 안과에서 수술 중 위중 상태에 빠진 8살 아들을 하늘로 떠나보내고 병원과의 소송을 준비 중인 A씨는 "누가 승산도, 기약도 없는 의료소송을 하고 싶겠나"라며 "고소를 하고 싶어서 한 게 아니라 아들의 사망이 미제로 남아버려 할 수 없이 하게 된 것"이라고 호소했다. A씨의 아들은 눈꺼풀 처짐으로 일상생활에 지장을 겪다 지난해 12월 전신마취 하에 수술을 하게 됐고, 전신마취 부작용인 '악성고열증'으로 대학병원으로 이송됐으나 중환자실 치료 중 숨졌다. 유족은 의사의 과실과 제대로 된 처치 여부를 의심했지만 의료지식이 전혀 없어 이를 입증하기는커녕 상황을 파악하기조차 힘들었다고 전했다. A씨는 "이름조차 처음 듣는 사망원인에 그게 정확히 무엇인지부터 직접 찾아봐야 했다"고 말했다. ADVERTISEMENT ADVERTISEMENT 그는 "의료지식이 없으니 '아이의 특이체질 때문에 부작용이 발생했으며 즉사할 것을 겨우 살려내서 대형병원에 이송시켰다'는 마취의 말이 진짜인지 아닌지 알 길이 없었다"고 말했다. 병원에서 관련 기록이나 정보를 얻어내기도 힘겨웠다. 수술 전 촬영에 동의했던 수술실 폐쇄회로(CC)TV 영상을 요구했으나 병원 측은 "착오로 녹화되지 않았다"고 답변했다. 병원 복도 CCTV 영상 또한 지금까지 받지 못했다. 유족은 결국 의료법 전문 변호사의 도움을 받기로 했다. 생업을 병행하고 남겨진 다른 아이를 돌보며 소송을 준비하는 데 한계를 느꼈기 때문이다. A씨는 "가족 전체의 삶이 무너졌다"고 호소했다. [한국환자단체연합회 제공. 재판매 및 DB 금지] [한국환자단체연합회 제공. 재판매 및 DB 금지] 정부는 지난 1일 민생토론회를 통해 의료인의 형사 처벌 부담을 덜어주는 의료사고처리특례법을 추진하겠다고 발표했다. 특례법의 요지는 책임보험·공제조합에 가입하면 피해자의 명시적 의사에 반해 의료사고 대상 공소를 제기할 수 없고, 피해 전액 보상 종합보험에 가입하면 공소 대상에서 제외시켜 주겠다는 것이다. 환자·의료소비자 단체는 즉각 반발했다. 이들은 "형사책임 면제 특례 도입에 앞서 의료사고 입증 책임을 의료인 측으로 전환하는 것이 전제돼야 한다"고 주장했다. 정부가 '충분한 환자 권리 구제를 전제로 특례를 도입하겠다'고 했지만 입증 책임을 전환하지 않으면 의료사고 피해자와 유족이 신속하고 충분한 배상을 받을 수 없는 환경이라는 것이다. 현행법상 의료사고를 둘러싼 민사소송에서는 환자 개인이 의사의 과실이나 과실·손해 간 인과 관계를 입증해야 한다. 전문성과 정보, 관련 지식이 압도적으로 부족한 환자 측에서 이를 입증하기란 쉽지 않다. 실제로 2021년 기준 의료과오 민사소송에서 원고 전부 승소율은 0.68%에 그쳤다. 변호사 도움을 받을 수 있다면 다행이지만, 통상보다 긴 소송 기간과 수임료가 부담돼 엄두도 못 내는 피해자들도 적잖다. 과실 입증을 하지 못하면 병원이 보험에 들어도 보험금을 받을 수 없다. 교통사고와 마찬가지로 의료사고 또한 고의나 과실이 있는 경우에만 보험금이 나오기 때문이다. 이에 환자단체들은 "입증 책임이 피해자 측에 있는 한 보상한도가 높아진다고 하더라도 피해자·유족의 상황은 현재와 크게 달라지지 않을 것"이라고 지적했다. 따라서 공소를 면제해 줄 것이라면 손해배상에 있어서 의료인과 병원이 스스로의 무과실을 입증하도록 해야 한다는 게 수요자 단체들의 주장이다. 이들은 의료사고처리특례법이 벤치마킹한 '교통사고처리특례법'의 관련법인 '자동차손해배상보장법'을 근거로 든다. 이 법에서는 운전자가 자신의 무과실을 증명한 경우에만 손해배상 책임이 면제된다고 명시해 놓았다. 교통사고에 있어서는 운전자에게 입증 책임과 형사 특례가 같이 적용되는 것이다. 경제정의실천시민연합의 신현호 변호사는 "교통사고특례에 자동차손해배상보장법상 입증 책임이 따르는 것처럼 의료인이 자신의 무과실을 입증하면 보험에 가입한 경우에만 책임을 면해 줘야 하며, 배상하는 경우 한도도 무제한으로 해 줘야 한다"고 주장했다. 정부의 목표는 '일단 소송까지 가는 일이 없도록 조정과 중재를 확대하겠다'는 것이다. 그러나 객관성 논란이 나오는 의료분쟁조정에 대해서는 의료계와 피해 환자들 모두 불만이 많다. 정부는 '감정부 구성을 합리화하고 감정 절차를 개선하겠다'고 했지만 새롭거나 구체적인 내용은 나오지 않았다. 의료분쟁조정은 의료기관의 거부로 시작조차 하지 못하고 각하되는 경우도 많다. 한국의료분쟁조정중재원 연보에 따르면 2022년 기준 조정 각하율은 38.9%였다. 한국환자단체연합회는 지난 1일 낸 성명에서 "의료사고 피해자도 의료인이 신이 아닌 이상 의료과실은 피할 수 없다는 사실을 알고 있다"며 "의료인이 충분히 사고의 내용과 경위를 설명하고 적정한 피해배상을 신속하게 한다면 상당수 피해자·유족은 그 상황을 받아들이고 형사고소를 하지 않을 것"이라고 말했다."""
    #
    result = await ai_client.request(request_text=request_text, system_prompt=system_prompt,
                                     model=LLMModel.OPENAI_GPT4o)

    # 산업별 초기 주식 가격 설정
    stocks = {
        "IT": 1000,
        "Hospital": 1000,
        "Financial": 1000,
        "Energy": 1000
    }

    # AI 요청 (json값)
    ai_result = parse(
        result
    )

    news_effects = ai_result

    # 30일간의 주식 변동 시뮬레이션
    days = 30
    stock_history = []

    for day in range(days):
        stocks = simulate_stock_changes(stocks, news_effects, day)
        stock_history.append(stocks.copy())

    # Pandas DataFrame으로 변환
    df = pd.DataFrame(stock_history)
    df.index.name = 'Day'
    print(df)

    # 주식 변동 결과 시각화
    df.plot(figsize=(12, 8))
    plt.title('Stock Price Simulation')
    plt.xlabel('date')
    plt.ylabel('stock price')
    plt.legend(title='industry')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
