import requests
import json
import os
from dotenv import load_dotenv

# 태초에 토큰 얻어오는 함수 (손볼때만 실행시키면 된다.)
def get_token():
    # env 변수 가져오기
    load_dotenv()

    APP_KEY = os.getenv("APP_KEY")
    CODE = os.getenv("CODE")
    REDIRECT_URI = os.getenv("REDIRECT_URI")

    # Get Token Request URL
    URL = "https://kauth.kakao.com/oauth/token"

    # Body Data
    data = {
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": CODE
    }

    # Request
    response = requests.post(URL, data=data)
    tokens = response.json()

    # 토큰 저장 : refresh token으로 갱신할때는 여기에 갱신
    with open("kakao_code.json","w") as fp:
        json.dump(tokens, fp)

    # 토큰 저장 : 이 함수를 실행할때 빼고는 읽기만 가능한 파일
    with open("original_kakao_code.json","w") as fp:
        json.dump(tokens, fp)

# 토큰 갱신 함수
def refresh_token():
    # json 파일에서 정보를 가져옴
    with open("original_kakao_code.json","r") as fp:
        tokens = json.load(fp)

    # env 변수 가져오기
    load_dotenv()

    APP_KEY = os.getenv("APP_KEY")

    # Refresh Token Request URL
    URL = "https://kauth.kakao.com/oauth/token"

    # Body Data
    data = {
        "grant_type": "refresh_token",
        "client_id": APP_KEY,
        "refresh_token": tokens["refresh_token"],
    }

    # Request
    response = requests.post(URL, data=data)

    # tokens 저장
    tokens = response.json()

    if "refresh_token" in tokens:
        # tokens를 original_kakao_code 파일에 저장
        with open("original_kakao_code.json","w") as fp:
            json.dump(tokens, fp)


    # tokens를 json 파일에 저장
    with open("kakao_code.json","w") as fp:
        json.dump(tokens, fp)

# 토큰이 유효한지 확인
def check_token_info():
    # json파일에서 정보를 가져옴
    with open("kakao_code.json","r") as fp:
        tokens = json.load(fp)

    # Access Token Info Request URL
    URL = "https://kapi.kakao.com/v1/user/access_token_info"

    # Headers
    headers = {
        "Authorization": "Bearer " + tokens['access_token']
    }

    # Request
    response = requests.get(URL, headers=headers)

    # 토큰 만료 시간
    return json.loads(response.text)
    

# 친구 목록 가져오기
def get_kakao_friends():
    # json 파일에서 정보를 가져옴
    with open("kakao_code.json","r") as fp:
        tokens = json.load(fp)

    # Get Kakao Friends List Request URL
    URL = "https://kapi.kakao.com/v1/api/talk/friends"

    # Headers
    headers = {
        "Authorization": "Bearer " + tokens['access_token']
    }
    
    # Request & Load to json
    friend_response = json.loads(requests.get(URL, headers=headers).text)

    # Get Friend List
    friend_list = friend_response.get("elements")

    # Get Friend uuids
    friend_uuid = [friend_list[0]["uuid"]]

    # Get json.dumps(friend_uuid)
    receiver_uuids = json.dumps(friend_uuid)

    return receiver_uuids

# 친구에게 카카오톡 메시지 전송
def send_kakao_message_to_friend(template_id, template_args):
    # json 파일에서 정보를 가져옴
    with open("kakao_code.json","r") as fp:
        tokens = json.load(fp)

    # Send Kakao Message To Friend Request URL
    URL = "https://kapi.kakao.com/v1/api/talk/friends/message/send"

    # Headers
    headers = {
        "Authorization": "Bearer " + tokens['access_token']
    }

    # Body Data
    data = {
        "receiver_uuids": get_kakao_friends(),
        "template_id":template_id,
        "template_args": json.dumps(template_args)
    }

    # Request
    response = requests.post(URL, headers=headers, data=data)

    # Log
    print("친구에게 카톡 보내기 : " + str(response.status_code))

# 나에게 카카오톡 메시지 전송
def send_kakao_message_to_me(template_id, template_args):
    # json 파일에서 정보를 가져옴
    with open("kakao_code.json","r") as fp:
        tokens = json.load(fp)

    # Send Kakao Message To Friend Request URL
    URL = "https://kapi.kakao.com/v2/api/talk/memo/send"

    # Headers
    headers = {
        "Authorization": "Bearer " + tokens['access_token']
    }

    # Body Data
    data = {
        "template_id":template_id,
        "template_args": json.dumps(template_args)
    }

    # Request
    response = requests.post(URL, headers=headers, data=data)

    # Log
    print("나에게 카톡 보내기 : " + str(response.status_code))


# 토큰 만료가 30분 이하면 token refresh 함수
def check_token_expired_before_start():
    token_dict = check_token_info()

    if "expires_in" in token_dict:
        if token_dict["expires_in"] < 3600:
            refresh_token()
            print("토큰 만료까지 1시간도 남지 않아, 토큰을 갱신했습니다.")
        else:
            print("토큰 만료까지 1시간 이상 남았습니다.")
            print("토큰을 갱신하지 않겠습니다.")
    else:
        refresh_token()
        print("토큰이 이미 만료되어 토큰을 갱신했습니다.")






# import datetime
# import schedule
# import time

# def test_schedule():
#     now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     send_kakao_message_to_me("51701",{"now":now})

# schedule.every().day.at("10:00").do(test_schedule)

# while True:
#     schedule.run_pending()
#     time.sleep(1)