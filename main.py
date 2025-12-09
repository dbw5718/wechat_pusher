import requests
import os
from datetime import datetime
import json
import traceback  # 用于打印详细异常栈

# ====================== 调试配置 ======================
# 是否开启详细调试（可通过环境变量控制，方便线上/测试切换）
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

def print_debug(msg):
    """封装调试打印函数，带时间戳"""
    if DEBUG_MODE:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] {timestamp} | {msg}")

# ====================== 核心逻辑（带调试） ======================
# 1. 读取并校验环境变量（脱敏打印）
print_debug("开始读取环境变量...")
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    USER_ID = os.environ["USER_ID"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]

    # 脱敏打印环境变量（仅展示前5位，避免泄露敏感信息）
    print_debug(f"APP_ID（前5位）: {APP_ID[:5] if len(APP_ID)>=5 else APP_ID}")
    print_debug(f"USER_ID（前5位）: {USER_ID[:5] if len(USER_ID)>=5 else USER_ID}")
    print_debug(f"TEMPLATE_ID（前5位）: {TEMPLATE_ID[:5] if len(TEMPLATE_ID)>=5 else TEMPLATE_ID}")
    print_debug("环境变量读取完成 ✅")
except KeyError as e:
    raise Exception(f"环境变量缺失！未找到: {e} | 当前已加载变量: {list(os.environ.keys())}")

# 2. 获取微信 Access Token（带请求/响应调试）
def get_access_token():
    print_debug("开始获取微信 Access Token...")
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    print_debug(f"Token请求URL: {url}")  # 注意：生产环境可注释，避免泄露secret

    resp = requests.get(url, timeout=10)
    print_debug(f"Token响应状态码: {resp.status_code}")
    print_debug(f"Token响应原始内容: {resp.text}")

    resp_json = resp.json()
    if 'access_token' in resp_json:
        token = resp_json['access_token']
        print_debug(f"Token获取成功（前10位）: {token[:10]} ✅")
        return token
    else:
        raise Exception(f"获取 Token 失败: {resp_json}")

# 3. 获取天气 (带API调试)
def get_weather():
    city = "北京"
    print_debug(f"开始获取[{city}]天气...")
    try:
        url = f"http://wthrcdn.etouch.cn/weather_mini?city={city}"
        print_debug(f"天气API请求URL: {url}")

        resp = requests.get(url, timeout=10)
        print_debug(f"天气API响应状态码: {resp.status_code}")
        print_debug(f"天气API响应原始内容: {resp.text}")

        resp_json = resp.json()
        if resp_json['status'] == 1000:
            today = resp_json['data']['forecast'][0]
            weather_info = {
                "city": city,
                "type": today['type'],
                "high": today['high'],
                "low": today['low']
            }
            print_debug(f"天气解析结果: {weather_info} ✅")
            return weather_info
        else:
            print_debug(f"天气API返回异常状态: {resp_json['status']}")
    except Exception as e:
        print_debug(f"获取天气失败 ❌: {str(e)} | 异常栈: {traceback.format_exc()}")

    # 兜底返回
    fallback_weather = {"city": city, "type": "未知", "high": "-", "low": "-"}
    print_debug(f"使用兜底天气数据: {fallback_weather}")
    return fallback_weather

# 4. 获取简易新闻 (带调试)
def get_news():
    print_debug("开始获取新闻内容...")
    news_content = "今天是个通过 GitHub Actions 自动部署的好日子！"
    print_debug(f"新闻内容: {news_content}")
    return news_content

# 5. 获取优惠信息 (带调试)
def get_discount():
    print_debug("开始获取优惠信息...")
    discount_content = "京东超市满199减100；Steam夏促开始啦！"
    print_debug(f"优惠信息: {discount_content}")
    return discount_content

# 6. 发送消息（带完整调试）
def send_message():
    print_debug("===== 开始执行消息推送流程 =====")

    # 获取Token
    token = get_access_token()
    push_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    print_debug(f"消息推送URL: {push_url}")

    # 获取各类内容
    weather_data = get_weather()
    news_content = get_news()
    discount_content = get_discount()

    # 构造当前日期
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_debug(f"当前构造日期: {current_date}")

    # 构造数据包
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
    print_debug(f"最终构造的推送数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    # 发送请求
    try:
        resp = requests.post(push_url, json=data, timeout=15)
        print_debug(f"推送请求响应状态码: {resp.status_code}")
        print_debug(f"推送请求响应原始内容: {resp.text}")

        resp_json = resp.json()
        if resp_json.get("errcode") == 0:
            print_debug("消息推送成功 ✅")
        else:
            print_debug(f"消息推送失败 ❌: {resp_json}")
        print(f"推送结果: {resp.text}")  # 保留原有打印
    except Exception as e:
        print_debug(f"推送请求异常 ❌: {str(e)} | 异常栈: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        send_message()
        print_debug("===== 消息推送流程执行完毕 =====")
    except Exception as e:
        print_debug(f"程序执行失败 ❌: {str(e)} | 完整异常栈: {traceback.format_exc()}")
        raise  # 抛出异常让GitHub Actions标记失败