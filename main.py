import requests
import os
from datetime import datetime
import json

# 从环境变量获取密钥（在 GitHub Secrets 中配置）
APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]
USER_ID = os.environ["USER_ID"]  # 关注者的 OpenID
TEMPLATE_ID = os.environ["TEMPLATE_ID"]

# 1. 获取微信 Access Token
def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    resp = requests.get(url).json()
    if 'access_token' in resp:
        return resp['access_token']
    else:
        raise Exception(f"获取 Token 失败: {resp}")

# 2. 获取天气 (示例使用中华万年历API，也可换成高德/和风天气)
def get_weather():
    city = "北京"
    try:
        # 这里仅作示例，实际可申请免费的天气 API key
        url = f"http://wthrcdn.etouch.cn/weather_mini?city={city}"
        resp = requests.get(url).json()
        if resp['status'] == 1000:
            today = resp['data']['forecast'][0]
            return {
                "city": city,
                "type": today['type'],
                "high": today['high'],
                "low": today['low']
            }
    except:
        return {"city": city, "type": "未知", "high": "-", "low": "-"}
    return None

# 3. 获取简易新闻 (示例)
def get_news():
    # 这里可以接入天行数据、聚合数据等新闻API
    # 或者简单的爬虫
    return "今天是个通过 GitHub Actions 自动部署的好日子！"

# 4. 获取优惠信息 (示例)
def get_discount():
    return "京东超市满199减100；Steam夏促开始啦！"

# 5. 发送消息
def send_message():
    token = get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"

    weather_data = get_weather()
    news_content = get_news()
    discount_content = get_discount()

    # 构造当前日期
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构造数据包，对应模板中的 {{key.DATA}}
    data = {
        "touser": USER_ID,
        "template_id": TEMPLATE_ID,
        "data": {
            "date": {"value": current_date, "color": "#173177"},
            "city": {"value": weather_data['city'], "color": "#173177"},
            "weather": {"value": f"{weather_data['type']} {weather_data['low']} {weather_data['high']}", "color": "#00FF00"},
            "news": {"value": news_content, "color": "#FF0000"},
            "discount": {"value": discount_content, "color": "#FFD700"}
        }
    }

    resp = requests.post(url, json=data)
    print(f"推送结果: {resp.text}")

if __name__ == "__main__":
    send_message()