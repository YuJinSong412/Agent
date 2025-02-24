from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from third_parties.linkedin import scrape_linkedin_profile

from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent

from output_parsers import summary_parser

def ice_break_with(name: str) -> str:
    linkedin_username = linkedin_lookup_agent(name=name)
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_username, mock=True)
    
    summary_template = """
        given the Linkedin information {information} about a person from I want you to create:
        1. a short summary
        2. two interesting facts about them
        
        Use information from Linkedin
        \n{format_instructions}
    """
  
    #pydantic 객체를 가져와 스키마를 추출하고 위 format_instructions에 삽입할 것
    summary_prompt_template = PromptTemplate(input_variables=["information"], template=summary_template,partial_variables={"format_instructions":summary_parser.get_format_instructions()})
    llm = ChatOllama(model="llama3.1:latest", temperature=0)
    
    
    chain = summary_prompt_template | llm | summary_parser
    
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url="https://www.linkedin.com/in/eden-marco/", mock=True)
    res = chain.invoke(input={"information": linkedin_data})
    
    print(res)


if __name__ == '__main__':

    print("Ice Breaker Enter")
    ice_break_with(name="Eden Marco")
    