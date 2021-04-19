import requests
import json
import os
from dotenv import load_dotenv

# env 변수 가져오기
load_dotenv()
SLACK_ZUM_URL = os.getenv("SLACK_ZUM_URL")
SLACK_LETTER_LOG_URL = os.getenv("SLACK_LETTER_LOG_URL")


# ZUM 크롤링 시작
def slack_zum_start(time):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "ZUM 실시간 검색어 크롤링 시작",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "현재시각 : " + time,
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    response = requests.post(SLACK_ZUM_URL, json=data)
    print("Slack Zum Start Response : " + response.text)

# ZUM 크롤링 성공
def slack_zum_success(text):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "ZUM 실시간 검색어 Top10",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    response = requests.post(SLACK_ZUM_URL, json=data)
    print("Slack Zum Success Response : " + response.text)

# ZUM 크롤링 실패
def slack_zum_failure():
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "ZUM 실시간 검색어 크롤링 실패",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "크롤링을 실패했습니다.",
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    response = requests.post(SLACK_ZUM_URL, json=data)
    print("Slack Zum Failure Response : " + response.text)

# 실제 인편 TEXT
def slack_real_letter_text(index, text):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"실제 인편 내용 ({index})" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_ZUM_URL, json=data)
    print("Slack Real Letter Text Response : " + response.text)


# 인편 전송 시작
def slack_camp_start(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 인편 전송 시작" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님에게 인편 전송을 시작합니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Letter Start Response : " + response.text)

# 더캠프 카페 개설 전
def slack_camp_no_cafe(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 카페 개설 전" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 카페가 아직 개설 전입니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp No Cafe Response : " + response.text)

# 더캠프 카페 개설 완료 상태
def slack_camp_activate_cafe(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 카페 개설 완료" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 카페가 개설되었습니다. 가입 후 인편 전송하겠습니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Activate Cafe Response : " + response.text)

# 더캠프 카페 개설 에러
def slack_camp_error_cafe(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 카페 개설 에러" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 카페에서 에러가 발생했습니다. 존재 할 수 없는 상태입니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Error Cafe Response : " + response.text)

# 더캠프 인편 진행도
def slack_camp_progress(name, all, index):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 인편 전송 진행도({index}/{all})" ,
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Progress Response : " + response.text)

# 더캠프 인편 완료
def slack_camp_success(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 인편 전송 성공" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 인편이 성공적으로 전송되었습니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Success Response : " + response.text)

# 더캠프 인편 실패
def slack_camp_failure(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 인편 전송 실패" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 인편 전송 실패했습니다.\n 카페 개설 전일 확률이 높습니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Failure Response : " + response.text)

# 더캠프 인편 에러
def slack_camp_error(name):
    data = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{name}님 : 인편 전송 에러" ,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{name}님의 인편 전송 에러가 발생했습니다.",
                }
            },
            {
                "type":"divider"
            }
        ]
    }

    response = requests.post(SLACK_LETTER_LOG_URL, json=data)
    print("Slack Camp Error Response : " + response.text)
