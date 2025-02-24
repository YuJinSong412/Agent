
import re
import json
from typing import Any
from pydantic import BaseModel, Field, ValidationError

########################################
# 1) 우리가 원하는 최종 Pydantic 모델
########################################
class Summary(BaseModel):
    summary: str
    facts: list[str]


########################################
# 2) 강화된 커스텀 파서
########################################
class MaxBruteForceParser:
    """
    Tries multiple regex extraction strategies to find JSON
    among code blocks or random text that LLM might produce.
    """

    def parse(self, text: str) -> Summary:
        """
        Main entry: tries multiple strategies to extract JSON from text.
        If everything fails, raises ValueError.
        """

        # 1) Step A: Try direct JSON parse (maybe the LLM gave pure JSON)
        result = self._try_direct_json(text)
        if result:
            return result

        # 2) Step B: Try to find ```json { ... } ```
        result = self._try_json_block(text)
        if result:
            return result

        # 3) Step C: Try to find "This code will output the following JSON:" pattern
        result = self._try_this_code_block(text)
        if result:
            return result

        # 4) Step D: Try to find "json.dumps({ ... })" in python code
        result = self._try_json_dumps_pattern(text)
        if result:
            return result

        # If all attempts fail
        raise ValueError("Could not extract valid JSON from LLM output:\n" + text)

    ###################################
    # Implementation of each step
    ###################################

    def _try_direct_json(self, text: str) -> Summary | None:
        """Try to parse the entire text as JSON."""
        text_stripped = text.strip()
        if not (text_stripped.startswith("{") and text_stripped.endswith("}")):
            return None
        try:
            data = json.loads(text_stripped)
            return Summary(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def _try_json_block(self, text: str) -> Summary | None:
        """
        Find triple-backtick + json: ```json ... ```
        Capture the inside { ... } and parse.
        """
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            return None

        json_str = match.group(1).strip()
        try:
            data = json.loads(json_str)
            return Summary(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def _try_this_code_block(self, text: str) -> Summary | None:
        """
        Find 'This code will output the following JSON:' and capture subsequent ```json block```
        """
        pattern = r"This code will output the following JSON:\s*```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            return None

        json_str = match.group(1).strip()
        try:
            data = json.loads(json_str)
            return Summary(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def _try_json_dumps_pattern(self, text: str) -> Summary | None:
        """
        Find 'json.dumps({ ... })' inside python code block and parse the {...} part
        """
        # 1) find code block
        code_block_pattern = r"```python\s*(.*?)\s*```"
        code_match = re.search(code_block_pattern, text, flags=re.DOTALL)
        if not code_match:
            return None

        code = code_match.group(1)

        # 2) inside the python code, find "json.dumps({ ... })"
        dumps_pattern = r"json\.dumps\s*\(\s*(\{.*?\})\s*\)"
        dumps_match = re.search(dumps_pattern, code, flags=re.DOTALL)
        if not dumps_match:
            return None

        json_str = dumps_match.group(1).strip()
        try:
            data = json.loads(json_str)
            return Summary(**data)
        except (json.JSONDecodeError, ValidationError):
            return None
