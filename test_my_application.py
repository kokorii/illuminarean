import pytest
from playwright.sync_api import Playwright, sync_playwright, Page, Browser, BrowserContext


class Testcase:
    def __init__(self, url:str, name:str, email, idea, playwright: Playwright):
        self.url: str = url
        self.name: str = name
        self.email: str = email
        self.idea: str = idea
        self.browser: Browser = playwright.chromium.launch(headless=True)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page

    def open_browser(self):
        self.context.set_default_timeout(timeout=10000.0)
        self.page = self.context.new_page()

    def go_to_page(self):
        self.page.goto(self.url)
        # print("go home")
        self.page.get_by_label("company:close_modal").click()
        # print("close modal")
        self.page.get_by_label("a11y:Contact").click()
        # print("go contact")

    def fill_with_given_conditions(self):
 
        if self.name is not None:
            self.page.get_by_label("이름").click()
            self.page.get_by_label("이름").fill(self.name)
            # print("fill name")

        if self.email is not None:
            self.page.get_by_label("이메일").click()
            self.page.get_by_label("이메일").fill(self.email)
            # print("fill email")

        if self.idea is not None:
            self.page.get_by_label("아이디어").click()
            self.page.get_by_label("아이디어").fill(self.idea)
            # print("fill idea")


    def check_button_status(self):
        if self.page.get_by_role("button", name="의견 나누기").is_enabled():
            return True
        else:
            return False

    def close_browser(self):
        # print("context, browser 를 종료합니다.")

        if self.context is not None:
            self.context.close()
        
        if self.browser is not None:
            self.browser.close()

########################################################################################################
# case 분할
# 입력칸은 이름, 이메일, 아이디어칸 3개로 입력에 대해 8가지 경우의 수가 있으며
# "의견 나누기" 버튼이 활성화 되는 경우의 수는 입력칸에 올바른 입력값이 3개가 입력 되는 경우 단 1개이다.

# 전체 경우의 수와 기대값
# o : 올바른 입력값
# x : 올바르지 않은 입력값(ex 빈칸, 이메일형식에 맞지않는 이메일 등)
# 기대결과 : 버튼 활성화 여부
# case| 이름  |  이메일  |아이디어| 기대결과
#    |------|--------|------| ------
#  1 |  o   |   x    |  x   |   x
#  2 |  o   |   x    |  o   |   x
#  3 |  o   |   o    |  x   |   x
#  4 |  o   |   o    |  o   |   o         -> 이 경우만 "의견 나누기" 버튼이 활성화 되며, 나머지 모두 비활성화 상태여야 한다.
#  5 |  x   |   x    |  x   |   x
#  6 |  x   |   x    |  o   |   x
#  7 |  x   |   o    |  x   |   x
#  8 |  x   |   o    |  o   |   x
########################################################################################################

test_cases = [
        # 1
        {
            "name": "kokori",
            "email": "Invalid format of email",
            "idea": None,
            "expect": False,
        },
        # 2
        {
            "name": "이름입니다",
            "email": "이건 올바르지 않은 이메일주소이다",
            "idea": "어떤 의견을 내야 좋을까?",
            "expect": False,
        },
        # 3
        {"name": "제니", "email": "test@test.net", "idea": None, "expect": False},
        # 4
        {
            "name": "김연아",
            "email": "test@test.co.kr",
            "idea": "!@#$!@$!@$!@#^%#$&$&*#@#$%",
            "expect": True,
        },
        # 5
        {"name": None, "email": "   ", "idea": None, "expect": False},
        # 6
        {"name": "", "email": "한글", "idea": "정말 이게 최선일까 ...", "expect": False},
        # 7
        {
            "name": "",
            "email": "test@test.co.kr",
            "idea": "19293582835",
            "expect": False,
        },
        # 8
        {
            "name": None,
            "email": "test@test.net",
            "idea": "올바른 아이디어 제시하기!",
            "expect": False,
        },
        # extra case 1
        # 이름에 정수(스트링)가 들어갈 수 있을까? -> yes, result true
        {
            "name": "1002383849293",
            "email": "test@test.co.kr",
            "idea": "19293582835",
            "expect": False,
        },  
        
        # extra case 2
        # 이름에 특수문자가 들어갈 수 있을까? -> yes, result true
        {
            "name": "@#$@#$!#%!$%//",
            "email": "test@test.net",
            "idea": "올바른 아이디어 제시하기!",
            "expect": False,
        },  
        
        # extra case 3
        # 9. 입력칸에 스크립트 넣어 보고싶어요,,,,,,,,,,,,,, (XSS 처리 확인 필요)
        # extra case 4 
        # 10. MAX Byte check: 스펙으로 정의된 최대 글자수를 넘지 않고 있는지 검증 필요
    ]

@pytest.mark.parametrize("test_case", test_cases)
def test_contact_page_input_form(test_case):  

    url = "https://www.illuminarean.com/"

    # given
    name: str = test_case["name"]
    email: str = test_case["email"]
    idea: str = test_case["idea"]

    # when
    with sync_playwright() as p:
        testcase: Testcase = Testcase(url, name, email, idea, p)
        try:
            print("testcase 생성")
            testcase.open_browser()
            
            print("browser open")
            testcase.go_to_page()
            
            print("go to contact page")
            testcase.fill_with_given_conditions()
            
            print("fill with given conditions")

            button_status = testcase.check_button_status()
            print("check button status")
            
    #then
            #test result
            #print(f"Testcase {idx+1}: {button_status}")
            assert button_status == test_case["expect"]

        finally:
            testcase.close_browser()
