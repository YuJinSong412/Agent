import os
from dotenv import load_dotenv

load_dotenv()

from typing import List, Tuple

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

# 커스텀 파서: LLM 출력이 코드 + JSON일 때 JSON만 파싱
from custom_json_parser import JSONBlockParser, Summary

from third_parties.linkedin import scrape_linkedin_profile
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent


####################################
# 추가 예시: Pydantic 모델(Interests, IceBreakers) 
# 간단히 topics_of_interest, ice_breakers 필드만
####################################
from pydantic import BaseModel

class Interests(BaseModel):
    topics_of_interest: List[str]

    def to_dict(self):
        return {"topics_of_interest": self.topics_of_interest}

class IceBreakers(BaseModel):
    ice_breakers: List[str]

    def to_dict(self):
        return {"ice_breakers": self.ice_breakers}


def ice_break_with(name: str) -> Tuple[Summary, Interests, IceBreakers, str]:
    """
    1) linkedin_lookup_agent 로 프로필 URL 획득
    2) scrape_linkedin_profile 로 프로필 정보(Mock)
    3) LLM에게 요약 + 흥미로운 사실 2가지 생성 요청
    4) JSONBlockParser 로 파싱 => Summary 모델
    5) Interests, IceBreakers는 예시로 임의값
    6) Profile Picture URL도 임시 또는 scrape 결과에 따라 세팅
    """

    # 1) LinkedIn 프로필 URL 찾기
    linkedin_url = linkedin_lookup_agent(name)
    # 2) LinkedIn 데이터 스크래핑 (mock=True는 테스트용)
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_url, mock=True)

    # 3) PromptTemplate
    summary_template = """
        You are a helpful assistant.
        You MUST provide valid JSON inside a single code block: ```json {{ ... }} ```
        No extra explanation. The JSON must contain "summary" (string) and "facts" (array of 2 items).

        Given the LinkedIn info: {information}
        Create:
        1. A short summary (summary field)
        2. Two interesting facts (facts array)
"""

    prompt = PromptTemplate(
        input_variables=["information"],
        template=summary_template
    )

    # 4) LLM 설정
    llm = ChatOllama(
        model="llama3.1:latest",
        temperature=0,
        # stop=["```", "Here is the code"]  # 필요 시
    )

    # 커스텀 파서로 JSON만 추출
    parser = JSONBlockParser(pydantic_object=Summary)

    # 체인 연결
    chain = prompt | llm | parser

    result = chain.invoke({"information": linkedin_data})
    # result는 Summary(BaseModel) 객체 (summary, facts)

    # 5) Interests, IceBreakers는 단순히 하드코딩 예시
    interests = Interests(topics_of_interest=[
        "GenAI", "Cloud Computing", "Udemy Course Creation"
    ])
    ice_breakers = IceBreakers(ice_breakers=[
        "What's your favorite side project recently?",
        "Have you tried any new AI tools lately?"
    ])

    # 6) 프로필 사진 URL (mock). 실제 LinkedIn 프로필 사진 URL이 없으니 예시로 대체
    profile_pic_url = "https://via.placeholder.com/300x300.png?text=Eden+Marco"

    return result, interests, ice_breakers, profile_pic_url


if __name__ == '__main__':
    summary_model, interests_model, icebreakers_model, pic_url = ice_break_with("Eden Marco")

    print("=== Summary ===")
    print(summary_model.summary)
    print("\n=== Interesting Facts ===")
    for f in summary_model.facts:
        print(f)

    print("\n=== Profile Pic URL ===")
    print(pic_url)

    print("\n=== Interests ===")
    print(interests_model.topics_of_interest)

    print("\n=== Ice Breakers ===")
    print(icebreakers_model.ice_breakers)
