from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import datetime
from gensim.summarization.summarizer import summarize
from newspaper import Article
import os
from dotenv import load_dotenv
from slack import slack_zum_success

# env 변수
load_dotenv()

CHROME_DRIVER_ONPIA_URL = os.getenv("CHROME_DRIVER_ONPIA_URL")

# 실검 스크래퍼
def ZUM_scrapper():
    # 현재 날짜 구하기
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

    # 크롬 드라이버 위치
    chromedriver = CHROME_DRIVER_ONPIA_URL

    # 크롬 드라이버 옵션
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920,1080')

    driver = webdriver.Chrome(chromedriver, options=options)
    driver.implicitly_wait(5)

    driver.get('https://zum.com/#!/home')

    # 실검 링크 리스트
    href_list = []

    # 실검 리스트
    silgum_list = []

    # 크롤링 실패 뉴스
    error_company = []

    # 기사 개수 카운트
    article_num = 0

    # 결과
    result = []

    # 검색 순위
    rank = 1

    # 요약 로그
    summary_log = {}

    # 메인페이지에서 실시간 검색어 탐색
    wrap_container = driver.find_element_by_id("wrap_container")
    issue_keyword_total = wrap_container.find_element_by_class_name("issue_keyword_total")
    rank_list = issue_keyword_total.find_element_by_class_name("rank_list")
    d_rank = rank_list.find_elements_by_class_name("d_rank")

    # 실검 링크 리스트와 실검 리스트 완성
    for item in d_rank:
        a_tag = item.find_element_by_class_name("d_btn_keyword")
        href = a_tag.get_attribute("href")
        href_list.append(href)

        silgum = a_tag.find_element_by_class_name("keyword").text
        silgum_list.append(silgum)


    # 내용 크롤링
    for href,silgum in zip(href_list, silgum_list):
        driver.implicitly_wait(5)
        driver.get(href)

        news_obj = {}

        news_title_xpath = f'//*[@id="newsItemUl"]/li[1]/dl/dt/a[@class="report-link"]'
        news_title = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, news_title_xpath)))
        news_href = news_title.get_attribute("href")

        # 내용 요약 (라이브러리 사용)
        article = Article(news_href, language='ko')
        article.download()
        try:
            article.parse()
            silgum_and_title = f"{rank}. {silgum}\n[{news_title.text}]\n"
            article_summary = article.text

            if len(article.text) > 1498 - len(silgum_and_title):
                ratio = round((1498 - len(silgum_and_title))/len(article.text),2)
                article_summary = summarize(article.text, ratio=ratio)
                if article_summary:
                    summary_log[f"rank{rank}"] = f"{ratio}비율"
                else:
                   article_summary = article.text

            # 1500자를 넘지 않게 커트해줌
            if len(silgum_and_title) + len(article_summary) > 1498:
                article_summary = article_summary.replace("\t","")[:1498]

            # 뉴스 리스트에 정보를 넣어줌
            news_obj["title"] = news_title.text
            news_obj["article"] = article_summary
            news_obj["URL"] = news_href
            article_num = article_num + 1 
        except Exception as error:
            news_obj["title"] = news_title.text
            news_obj["article"] = "크롤링 실패"
            news_obj["URL"] = news_href
            error_company.append({"title": f"{rank}. {silgum} : {news_title.text}", "log": f"Error : {error}"})

        # 결과 리스트에 최종 결과물을 넣어줌
        result.append({
            "rank": rank,
            "word": silgum,
            "news": news_obj,
        })
        rank = rank + 1

    # 결과 print
    print("현재시간 : " + nowDatetime)  
    print("ZUM 실시간 검색어 Top10 요약")
    print(f"기사 개수 : {article_num}")
    print(f"크롤링 실패 뉴스 : {error_company}")
    print(f"요약 로그 : {summary_log}")

    # ZUM SLACK TEXT
    ZUM_SLACK_TEXT = ""

    # Slack에 로깅할 문자열 만들기
    for word in result:
        ZUM_SLACK_TEXT = ZUM_SLACK_TEXT + str(word["rank"]) + ". " + word["word"] + "\n" + "<" + word["news"]["URL"] + "|" + word["news"]["title"] + ">" + "\n\n"

    # 슬랙에 로깅
    slack_zum_success(ZUM_SLACK_TEXT)

    return result
