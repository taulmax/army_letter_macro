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

    # 내용에 들어갈 문자열들
    first_letter_contents = ""
    second_letter_contents = ""

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

        # news_ul = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.ID, "newsItemUl"))) 
        # news_li = news_ul.find_elements_by_xpath('//*[@id="newsItemUl"]/li')
        news_list = []

        news_title_xpath = f'//*[@id="newsItemUl"]/li[1]/dl/dt/a[@class="report-link"]'
        news_title = WebDriverWait(driver,timeout=5).until(EC.presence_of_element_located((By.XPATH, news_title_xpath)))
        news_href = news_title.get_attribute("href")

        # 내용 요약 (라이브러리 사용)
        article = Article(news_href, language='ko')
        article.download()
        try:
            article.parse()
            article_summary = ""
            
            # 단어 수로 먼저 요약
            for i in range(30):
                num = (i+12)*5
                article_summary = summarize(article.text, word_count=int(num))
                if article_summary:
                    summary_log[f"rank{rank}"] = f"{rank}. {num}단어"
                    break
                    
            # 단어 수로 요약하는게 실패했을 경우, 비율로 요약
            if not article_summary:
                for j in range(10):
                    ratio_num = (j+1) * 0.3
                    article_summary = summarize(article.text, ratio=ratio_num)
                    if article_summary:
                        summary_log[f"rank{rank}"] = f"{rank}. {ratio_num}비율"
                        break

            # 둘 다 실패했을경우 그냥 본문 가져오기
            if not article_summary:
                article_summary = article.text
                summary_log[f"rank{rank}"] = f"{rank}. 본문 가져옴"

            # 한 기사당 300자를 넘지 않게 커트해줌
            silgum_and_title = f"{rank}. {silgum}\n[{news_title.text}]\n"
            content_letter_count = 298 - len(silgum_and_title)
            
            if len(article_summary) > content_letter_count:
                article_summary = article_summary.replace("\t","").replace("\n","")[:content_letter_count]

            # 뉴스 리스트에 정보를 넣어줌
            news_list.append({"title":news_title.text, "article": article_summary})
            article_num = article_num + 1 
        except Exception as error:
            news_list.append({"title":news_title.text, "article": "크롤링 실패"})
            error_company.append({"title": f"{rank}. {silgum} : {news_title.text}", "log": f"Error : {error}"})

        # 결과 리스트에 최종 결과물을 넣어줌
        result.append({
            "rank": rank,
            "word": silgum,
            "news": news_list,
        })
        rank = rank + 1

    # 결과 print
    print("현재시간 : " + nowDatetime)  
    print("ZUM 실시간 검색어 Top10 요약")
    print(f"기사 개수 : {article_num}")
    print(f"크롤링 실패 뉴스 : {error_company}")
    print(f"요약 로그 : {summary_log}")

    # 내용에 붙여넣을 문자열 만들기
    for idx,word in enumerate(result,1):
        if idx <= 5:
            first_letter_contents = first_letter_contents + str(word["rank"]) + ". " + word["word"] + " : "
        else:
            second_letter_contents = second_letter_contents + str(word["rank"]) + ". " + word["word"] + " : "
        for news in word["news"]:
            if idx <= 5:
                first_letter_contents = first_letter_contents + "[" + news["title"] + "] - " + news["article"] + "\n"
            else:
                second_letter_contents = second_letter_contents + "[" + news["title"] + "] - " + news["article"] + "\n"

    # 최종적으로 넘길 정보
    ZUM_result = [
        {
            "title": "ZUM 실시간 검색어 TOP10 요약 1~5위 " + nowDatetime,
            "contents": first_letter_contents
        },
        {
            "title": "ZUM 실시간 검색어 TOP10 요약 6~10위 " + nowDatetime,
            "contents": second_letter_contents
        }
    ]

    return ZUM_result