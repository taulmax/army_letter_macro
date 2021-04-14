from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from kakao import send_kakao_message_to_me
import time
import os
from dotenv import load_dotenv

# env 변수
load_dotenv()

CHROME_DRIVER_ONPIA_URL = os.getenv("CHROME_DRIVER_ONPIA_URL")
LETTER_PROGRESS = os.getenv("LETTER_PROGRESS")
MY_CAMP_ID = os.getenv("MY_CAMP_ID")
MY_CAMP_PASSWORD = os.getenv("MY_CAMP_PASSWORD")

# 인편 보내기 로직
def send_internet_letter(soldier_name, final_list):
    chromedriver = CHROME_DRIVER_ONPIA_URL
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('window-size=1920,1080')

    driver = webdriver.Chrome(chromedriver, options=options)
    driver.implicitly_wait(5)

    driver.get('https://www.thecamp.or.kr/login/viewLogin.do')
    time.sleep(1)

    # 아이디 입력
    input_id = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userId"]'))) 
    time.sleep(1)
    input_id.send_keys(MY_CAMP_ID)

    # 패스워드 입력
    input_pw = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userPwd"]'))) 
    time.sleep(1)
    input_pw.send_keys(MY_CAMP_PASSWORD)
    time.sleep(1)

    # 로그인
    login = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="emailLoginBtn"]')))
    time.sleep(1)
    login.click()
    time.sleep(1)

    # 카페 가입하기 (아마 까페 개설 확인까지 해야될거같긴한데 그건 민준이꺼 보고 한번 판단해보도록 하자)

    # 카페 클릭
    cafe = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, '/html/body/header/div/div/ul/li[1]/a'))).get_attribute("href")
    time.sleep(1)
    driver.get(cafe)
    time.sleep(1)

    # 추천 카페에서 버튼 이름이 카페확인이냐 가입하기냐에 따라 다르게 해야할듯 element.text로 나중에 한번 체크하는거 만들어봐야겠다.
    cafe_container = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]')))
    time.sleep(1)
    card_list = cafe_container.find_elements_by_class_name("cafe-card-box")
    time.sleep(1)

    target_card = None

    # 내가 편지를 보내고 싶은 군인만 찾는 로직. 여러 카드들 중에 이름만 따와서 이름 비교.
    for card in card_list:
        card_title = card.find_element_by_class_name("id")
        real_title = card_title.text
        if real_title == "":
            pass
        else:
            real_name = real_title.split(' ')[0]
            if real_name == soldier_name:
                target_card = card

    # 내가 찾는 군인의 상태를 알기위해, 카드의 버튼이 뭔지 알아본다.
    # 두 개면 인편을 보낼 수 있는 상태
    # 한 개면 인편을 보낼 수 없는 상태
    # 한 개일때, "카페 개설확인", "카페 가입" 이렇게 두 가지로 나뉜다.
    card_btn_wrap = target_card.find_element_by_class_name("btn-wrap")
    time.sleep(1)
    card_btn_list = card_btn_wrap.find_elements_by_tag_name("a")
    time.sleep(1)

    # 인편을 보낼 수 있는 상태
    if len(card_btn_list) == 2:
        card_btn_list[0].click()
        time.sleep(1)
        write_letter_btn = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div[3]/button')
        write_letter_btn.click()
        time.sleep(1)

        # 여기서부터 반복
        for idx, item in enumerate(final_list,1):
            letter_title = driver.find_element_by_xpath('//*[@id="sympathyLetterSubject"]')
            letter_iframes = driver.find_elements_by_tag_name('iframe')

            # 제목 입력
            letter_title.send_keys(item["title"])

            # iframe 탐색 후 내용 입력
            for i, iframe in enumerate(letter_iframes):
                try:
                    driver.switch_to_frame(letter_iframes[i])
                    try:
                        html = driver.find_element_by_xpath('/html[@dir="ltr"]')
                        contents = html.find_element_by_tag_name('p')
                        contents.click()
                        contents.send_keys(item["contents"])
                        time.sleep(3)
                    except:
                        driver.switch_to_default_content()
                except:
                    driver.switch_to_default_content()
                    pass

            time.sleep(1)

            # 인편 보내기 버튼 클릭
            final_send = driver.find_element_by_xpath('/html/body/div[1]/div[3]/section/div[2]/a[3]')
            final_send.click()
            time.sleep(2)
            send_kakao_message_to_me(LETTER_PROGRESS, {"all": len(final_list), "current_idx": idx})

    # 인편을 보낼 수 없는 상태
    elif len(card_btn_list) == 1:
        card_btn_list[0].click()
        time.sleep(3)
        alert = driver.switch_to.alert
        message = alert.text.split('\n')[0]
        print(message)
        if message == "카페가 아직 개설전 입니다":
            solider_state_log = "카페 개설 X"

    # 이런 상태는 있으면 안된다. 에러가 난것
    else:
        print("아마 에러인듯")
        solider_state_log = "나올수 없는 상태"


