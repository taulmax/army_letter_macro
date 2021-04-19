from scrapper import ZUM_scrapper
from camp import try_send_letter
import os
from dotenv import load_dotenv
from kakao import send_kakao_message_to_me, check_token_expired_before_start
import datetime
import schedule
import time
from slack import slack_zum_start, slack_zum_failure, slack_camp_start, slack_camp_failure, slack_camp_error

# env 변수
load_dotenv()

SCRAP_START = os.getenv("SCRAP_START")
SCRAP_SUCCESS = os.getenv("SCRAP_SUCCESS")
SCRAP_FAILURE = os.getenv("SCRAP_FAILURE")
LETTER_START = os.getenv("LETTER_START")
LETTER_SUCCESS = os.getenv("LETTER_SUCCESS")
LETTER_FAILURE = os.getenv("LETTER_FAILURE")
LETTER_ERROR = os.getenv("LETTER_ERROR")

ZUM = os.getenv("ZUM")

SOL1802 = os.getenv("SOL1802")
SOL5226 = os.getenv("SOL5226")
SOL4008 = os.getenv("SOL4008")
SOL0728 = os.getenv("SOL0728")
SOL0807 = os.getenv("SOL0807")

# ZUM 실검 군인 리스트
ZUM_SOL_LIST = [SOL1802, SOL5226, SOL4008, SOL0728, SOL0807]

# 현재 날짜 구하기
now = datetime.datetime.now()
nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

# 시작 함수
def init():
    # 카카오 토큰 만료 여부 확인 후 갱신
    check_token_expired_before_start()

    # 크롤링 시작 카톡 보냄
    send_kakao_message_to_me(SCRAP_START, {"target":ZUM})

    # 크롤링 시작 슬랙 보냄
    slack_zum_start(nowDatetime)

    # 최종 내용 리스트
    final_list = []

    # ZUM 크롤링 시도 (성공시 성공 카톡, 실패시 실패 카톡)
    try:
        ZUM_silgum = ZUM_scrapper()
        final_list = final_list + ZUM_silgum
        send_kakao_message_to_me(SCRAP_SUCCESS, {"target":ZUM})
    except:
        send_kakao_message_to_me(SCRAP_FAILURE, {"target":ZUM})
        slack_zum_failure()

    # 크롤링에 성공했으면 인편, 실패했으면 카카오 메시지 전송 후 끝
    # 추후에 스페어 인편이라도 준비해주면 좋을듯 하다.
    for sol in ZUM_SOL_LIST:
        if final_list:
            send_kakao_message_to_me(LETTER_START, {"name":sol})
            slack_camp_start(sol)
            try:
                try_send_letter(sol, final_list)
            except:
                send_kakao_message_to_me(LETTER_FAILURE, {"name":sol})
                slack_camp_failure(sol)
        else:
            send_kakao_message_to_me(LETTER_ERROR, {"name":sol})
            slack_camp_error(sol)
    

schedule.every().day.at("18:00").do(init)

while True:
    schedule.run_pending()
    time.sleep(1)
