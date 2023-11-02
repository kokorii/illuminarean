import re
import pytest, asyncio
from playwright.async_api import async_playwright, Playwright, Page, Browser, BrowserContext

class Testcase:
    def __init__(self, url:str, corpName:str, ceoName:str, bizType:str ,numOfMem:str , name:str, email:str,
                        phoneNumber:str, role:str, termsAgree:bool, personalInfoAgree:bool, playwright:Playwright):
                       
        self.url: str = url
        self.corpName: str = corpName
        self.ceoName: str = ceoName
        self.bizType:str = bizType
        self.numOfMem: str = numOfMem
        self.name: str = name
        self.email: str = email
        self.phoneNumber: str = phoneNumber
        self.role: str = role
        self.termsAgree: bool = termsAgree
        self.personalInfoAgree: bool = personalInfoAgree
        self.playwright: Playwright = playwright
        self.context: BrowserContext
        self.page: Page
        self.goodvibe_page: Page

    async def initialize(self):
        self.browser: Browser = await self.playwright.chromium.launch(headless=True)
        self.context: BrowserContext = await self.browser.new_context()
        
    async def go_to_goodvibe_free(self):
        self.page = await self.context.new_page()
        await self.page.goto(self.url)
        await self.page.get_by_label("company:close_modal").click()
        await self.page.get_by_label("a11y:Work").click()
        
        #go goodvibe works site and open new tab
        async with self.page.expect_popup() as new_page_info:
            await self.page.get_by_role("link", name="GOODVIBE WORKS 바로가기").click()
        self.goodvibe_page = await new_page_info.value

        #무료체험 신청 버튼 2가지 -> 상단 배너, 본문 버튼
        await self.goodvibe_page.get_by_role("banner").get_by_role("button", name="무료 체험 신청").click()

    async def fill_with_given_conditions(self):
        #회사명
        #await self.goodvibe_page.get_by_placeholder("30자 이내로 입력해주세요.").click()
        await self.goodvibe_page.get_by_placeholder("30자 이내로 입력해주세요.").fill(self.corpName)
        
        #대표명
        #await self.goodvibe_page.locator("#ceoName").click()
        await self.goodvibe_page.locator("#ceoName").fill(self.ceoName)

        #사업자유형
        await self.goodvibe_page.locator("#businessType div").first.click()
        await self.goodvibe_page.get_by_text(self.bizType, exact=True).click()

        #직원수
        await self.goodvibe_page.locator("#scale div").nth(4).click()
        await self.goodvibe_page.get_by_text(self.numOfMem, exact=True).dblclick()

        #담당자이름
        await self.goodvibe_page.locator("#name").fill(self.name)

        #이메일주소
        await self.goodvibe_page.get_by_placeholder("회사 이메일을 입력해주세요.").fill(self.email)

        #핸드폰번호
        await self.goodvibe_page.get_by_placeholder("숫자로 입력해주세요.").fill(self.phoneNumber)

        #담당업무
        
        #선택으로 1개(임의지정)
        await self.goodvibe_page.locator("button").filter(has_text="담당 업무를 1개 이상 선택해주세요.").click()
        await self.goodvibe_page.get_by_text("스타일리스트").click()

        #검색으로 한개
        await self.goodvibe_page.get_by_placeholder("업무명 검색").fill(self.role)
        await self.goodvibe_page.get_by_text(re.compile(self.role)).click()

        #등록
        await self.goodvibe_page.get_by_text("등록").click()

        #약관 및 개인정보방침 동의, 일단 다 동의
        if self.termsAgree == True:
            await self.goodvibe_page.get_by_label("서비스 이용약관 동의").check()
        
        if self.personalInfoAgree == True:
            await self.goodvibe_page.get_by_label("개인정보 취급방침 동의").check()
        
        
        print("이것저것 테스트했다")


    async def check_button_status(self):
        
        if self.goodvibe_page.get_by_text("무료 이용 신청").is_enabled():
            return True
        else:
            return False

    async  def close_browser(self):
        # print("context, browser 를 종료합니다.")

        if self.context is not None:
            await self.context.close()
        
        if self.browser is not None:
            await self.browser.close()

########################################################################################################
# case 분할
# 입력칸
# 회사명, 대표자명, 사업자 유형(드롭), 직원수(드롭), 담당자명, 이메일, 휴대폰번호, 담당업무(선택)
# 서비스 약관, 개인정보 취급 방침 각각 동의 버튼
#
# 입력에 따른 기대값
# * 필수입력칸이 지정되지 않아 "무료 이용 신청" 버튼 활성화 조건이 뭔지 모르겠음.
# * 임의로 전체 모든 값이 입력되고, 약관과 취급방침 모두 동의된 상태에서만 무료 이용 신청 버튼 활성화 되는 것으로 정의
# 활성화상태만 확인
# 테스트 케이스 추가 확장가능
########################################################################################################

test_cases = [
        # 1
        {
            "corpName": "NextTime",
            "ceoName": "I\'m 신뢰",
            "bizType": "개인",
            "numOfMem": "101-200 명",
            "name": "kokori",
            "email": "test@host.co.kr",
            "phoneNumber": "01012341231",
            "role": "임원",
            "termsAgree": True,
            "personalInfoAgree": True,
            "expect": True,
        }
    ]

@pytest.mark.parametrize("test_case", test_cases)
async def test_goodvibe_freeform(test_case):  

    url = "https://www.illuminarean.com/"

    # given
    corpName: str = test_case["corpName"]
    ceoName: str = test_case["ceoName"]
    bizType: str = test_case["bizType"]
    numOfMem: str = test_case["numOfMem"]
    name: str = test_case["name"]
    email: str = test_case["email"]
    phoneNumber: str = test_case["phoneNumber"]
    role: str = test_case["role"]
    termsAgree: bool = test_case["termsAgree"]
    personalInfoAgree: bool = test_case["personalInfoAgree"]


    # when
    async with async_playwright() as p:
        testcase: Testcase = Testcase(url, corpName, ceoName, bizType, numOfMem, name, email,
                                       phoneNumber, role, termsAgree, personalInfoAgree, p)
        try:
            await testcase.initialize()
            print("testcase 생성")

            await testcase.go_to_goodvibe_free()
            print("go to goodvibe works website")
            
            await testcase.fill_with_given_conditions()
            print("fill with given conditions")
            

            button_status = await testcase.check_button_status()
            print("check submit button status")
            
    #then
            #test result
            #print(f"Testcase {idx+1}: {button_status}")
            assert button_status == test_case["expect"]

        finally:
            await testcase.close_browser()
