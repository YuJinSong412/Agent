import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

from langchain_core.tools import Tool

#create_react_agent : 에이전트를 구동하기 위해 사용할 LLM을 받음. 
#도구들과 ReAct 프롬프트를 받게 되며 우리게 제공한 LLM과 도구들을 사용하는 ReACT 알고리즘 기반의 에이전트를 반환함  

#AgentExecutor : 에이전트의 런타임 즉, 우리의 프롬프트와 수행할 지시사항을 받아서 작업하는 객체
from langchain.agents import(
    create_react_agent, 
    AgentExecutor
)

from langchain import hub 
from tools.tools import get_profile_url_tavily

load_dotenv()


def lookup(name: str) -> str:
    llm = ChatOllama(model="llama3.1:latest", temperature=0)

    #프롬프트 템플릿에 제공할 템플릿 작성 
    template = """given the full name {name_of_person} I want you to get it me a link to their Linkedin profile page.
                          Your answer should contain only a URL"""
                        
                        
    #프롬프트 초기화
    prompt_template = PromptTemplate(
        template=template, input_variables=["name_of_person"]
    )
    #linkedin 프로필 페이지를 검색하는 구현 func
    #description중요. LLM이 이 도구를 사용할지 말지를 결정하는 기준. 헷갈리지 않고 LLM이 언제 어떤 도구를 사용해야 할지 알 수 있게 간결하지만 최대한 자세하게 적기.
    #에이전트가 추론 엔진에 따라 이 도구를 호출해야 한다고 결정하면 이 검색 함수를 실행할 것
    tools_for_agent = [
        Tool(
            name="Search Google 4 linkedin profile page",
            func=get_profile_url_tavily,
            description="useful for when you need get the Linkedin Page URL",
        )
    ]
    
    #react prompt 다운로드
    react_prompt = hub.pull("hwchase17/react") #LLM에 보내지는 프롬프트 
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True, max_iterations=3, handle_parsing_errors=True)

    result = agent_executor.invoke(
            input={"input": prompt_template.format_prompt(name_of_person=name)}
        )
    
    linked_profile_url = result["output"]
    return linked_profile_url

if __name__ == '__main__':
    print("start")
    linkedin_url = lookup(name="Eden Marco")
    print(linkedin_url)
    
#랭체인으로 ReAct 에이전트를 만드는 것. 
#도구 목록, 사용할 프롬프트, 그리고 LLM 제공함 