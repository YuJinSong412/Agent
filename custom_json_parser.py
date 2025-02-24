# [my_project/output_parsers/custom_json_parser.py]

import re
import json
from typing import List
from pydantic import BaseModel, Field, ValidationError

# langchain_core가 설치되어 있다면 import
# (설치 버전에 따라 경로가 다를 수도 있습니다)
from langchain_core.output_parsers import PydanticOutputParser


class Summary(BaseModel):
    """LLM이 생성하는 요약 정보를 담을 Pydantic 모델"""
    summary: str = Field(description="Short summary")
    facts: List[str] = Field(description="Two interesting facts")

    def to_dict(self):
        return {
            "summary": self.summary,
            "facts": self.facts
        }


class JSONBlockParser(PydanticOutputParser):
    """
    LLM 응답에서 ```json ... ``` 블록 안의 JSON만 추출해
    Summary 모델로 파싱하는 커스텀 파서.
    """

    def parse(self, text: str) -> Summary:
        # 1) 부모 클래스(기본 Pydantic 파서) 먼저 시도
        try:
            return super().parse(text)
        except Exception:
            pass  # 실패 시 아래 로직

        # 2) 정규식으로 ```json ... ``` 블록 찾아내기
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, flags=re.DOTALL)

        if not match:
            raise ValueError(
                "No valid ```json ... ``` block found in LLM output:\n" + text
            )

        # 3) 정규식 캡처 그룹 -> 실제 JSON 문자열
        json_str = match.group(1)

        # 4) json.loads + Pydantic 검증
        try:
            data = json.loads(json_str)
            return Summary(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(
                f"Failed to parse JSON from the code snippet:\n{json_str}\nError: {e}"
            )
