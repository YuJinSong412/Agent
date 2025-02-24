from typing import List, Dict, Any

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
#데이터 검증과 설정 관리를 도와주는 외부 라이브러리 스키마를 정의하고 스키마에 대한 입력을 검증할 수 있게 해줌.
#pydantic


#LLM의 답변을 파싱할 클래스인 summary
#pydantic 객체 생성 
class Summary(BaseModel):
    summary: str = Field(description="summary")
    facts: List[str] = Field(description="interesting facts about them")

    def to_dict(self) -> Dict[str, Any]:
        return {"summary": self.summary, "facts": self.facts}


##PydanticOutputParser클래스를 사용하고 summary 클래스 제공 
#이것은 LLM의 답변을 파싱하여 우리가 원하는 pydantic 객체임
summary_parser = PydanticOutputParser(pydantic_object=Summary)
