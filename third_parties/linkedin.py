import os
import requests
from dotenv import load_dotenv

load_dotenv()

#스크래핑을 수행하는 함수 정의
#http 요청만으로 LinkedIn 정보를 스크래핑해주는 proxy curl이라는 외부 API를 사용함 
#mock이 false일 경우 모킹과 로컬 개발에 사용하기 위해 부울 값을 지정함 
def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = False):
    """scrape information from LinkedIn profiles,
    Manually scrape the information from the LinkedIn profile"""
    
    if mock:
        linkedin_profile_url = "https://gist.githubusercontent.com/emarco177/0d6a3f93dd06634d95e46a2782ed7490/raw/fad4d7a87e3e934ad52ba2a968bad9eb45128665/eden-marco.json"
        response = requests.get(
            linkedin_profile_url,
            timeout=10,
        )
    else:
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        header_dic = {"Authorization": f'Bearer {os.environ.get("PROXYCURL_API_KEY")}'}
        response = requests.get(
                        api_endpoint,
                        params={"url": linkedin_profile_url},
                        headers=header_dic,
                        timeout=10,)
    #mock이 false인 경우에는 proxycurl 호출
    
#http 응답 받아 딕셔너리로 변환하고 반환

    data = response.json()
    data = {
        k: v
        for k,v in data.items()
        if v not in ([], "", "", None)
        and k not in ["people_also_viewed", "certifications"]
    }
    if data.get("groups"):
        for group_dict in data.get("groups"):
            group_dict.pop("profile_pic_url")
            
    return data

if __name__ == "__main__":
    print(
        scrape_linkedin_profile(
            linkedin_profile_url="https://www.linkedin.com/in/eden-marco/", mock=True
        )
    )