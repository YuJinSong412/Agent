import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from third_parties.linkedin import scrape_linkedin_profile

from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent

from output_parsers import summary_parser, Summary

from typing import Tuple
# information = """
# Elon Reeve Musk (/ˈiːlɒn mʌsk/; born June 28, 1971) is a businessman and senior advisor to the U.S. president, known for his key roles in Tesla, Inc., SpaceX, the Department of Government Efficiency (DOGE), and his ownership of Twitter. Musk is the wealthiest individual in the world; as of February 2025, Forbes estimates his net worth to be US$397 billion.

# Musk was born to an affluent South African family in Pretoria before immigrating to Canada, acquiring its citizenship from his mother. He moved to California in 1995 to attend Stanford University, and with his brother Kimbal co-founded the software company Zip2, which was acquired by Compaq in 1999. That same year, Musk co-founded X.com, a direct bank, that later formed PayPal. In 2002, Musk acquired U.S. citizenship, and eBay acquired PayPal. Using the money he made from the sale, Musk founded SpaceX, a spaceflight services company, in 2002. In 2004, Musk was an early investor in electric vehicle manufacturer Tesla and became its chairman and later CEO. In 2018, the U.S. Securities and Exchange Commission (SEC) sued Musk for fraud, alleging he falsely announced that he had secured funding for a private takeover of Tesla; he stepped down as chairman and paid a fine. Musk was named Time magazine's Person of the Year in 2021. In 2022, he acquired Twitter, and rebranded the service as X the following year. In January 2025, he was appointed head of Trump's newly created DOGE.

# His political activities and views have made him a polarizing figure. He has been criticized for making unscientific and misleading statements, including COVID-19 misinformation, affirming antisemitic and transphobic comments, and promoting conspiracy theories. His acquisition of Twitter was controversial due to a subsequent increase in hate speech and the spread of misinformation on the service. Musk has engaged in political activities in several countries, including as a vocal and financial supporter of U.S. president Donald Trump. He was the largest donor in the 2024 United States presidential election, and is a supporter of far-right activists, causes, and political parties.


# """

def ice_break_with(name: str) -> Tuple[Summary, str]:
    linkedin_username = linkedin_lookup_agent(name=name)
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_username, mock=True)
    
    summary_template = """
        You are a helpful assistant. You MUST follow these rules:

        1. Output must be valid JSON.
        2. Do NOT include any code block formatting such as triple backticks.
        3. Do NOT include any additional text or explanation outside the JSON.
        4. The JSON must follow the schema below exactly:

        {format_instructions}

        Now, given the Linkedin information {information} about a person,
        create:
        1. A short summary (summary field)
        2. Two interesting facts about them (facts array)

        Return only valid JSON.
    """
    # given the Linkedin information {information} about a person from I want you to create:
    #     1. a short summary
    #     2. two interesting facts about them
         
    #     Use information from Linkedin
    #     \n{format_instructions}
    
    
    
    #pydantic 객체를 가져와 스키마를 추출하고 위 format_instructions에 삽입할 것
    summary_prompt_template = PromptTemplate(input_variables=["information"], template=summary_template,partial_variables={"format_instructions":summary_parser.get_format_instructions()})
    # summary_prompt_template = PromptTemplate(input_variables=["information"], template=summary_template)
    
    llm = ChatOllama(model="llama3.1:latest", temperature=0)
    
    #chain = summary_prompt_template | llm | StrOutputParser()
    
    
    chain = summary_prompt_template | llm | summary_parser
    # chain = summary_prompt_template | llm
    
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url="https://www.linkedin.com/in/eden-marco/", mock=True)
    res:Summary = chain.invoke(input={"information": linkedin_data})

    return res, linkedin_data.get("profile_pic_url")

if __name__ == '__main__':

    print("Ice Breaker Enter")
    # print(os.getenv('OPENAI_API_KEY'))
    ice_break_with(name="Eden Marco")
    
    
    
#     문제점 정리
# 문제 핵심: LLM이 JSON 포맷 대신 파이썬 코드를 포함한 문자열을 응답 → json.loads(...) 시도 시 파싱 실패
# 결과: “Expecting value: line 1 column 1” 등 JSONDecodeError가 발생
# 즉, 모델이 “오직 JSON” 형태만 내놓아야 하는데, **“여전히 코드 블록+설명”**을 함께 내놓음으로써 파싱이 깨짐 

# 문제는 llama3.1이 출력할 때,

# 순수 JSON 형태가 아니라 파이썬 코드 블록을 포함하거나,
# “이런 식으로 쓰면 됩니다.”라고 부가 설명을 달아서,
# 최종적으로 JSON 파싱이 깨지는 경우가 자주 발생한다는 점

# https://github.com/langchain-ai/langchain/discussions/22103
#LLM(특히 Llama 계열)은 “코드와 설명을 덧붙여야 한다”고 추론하는 경우가 많음