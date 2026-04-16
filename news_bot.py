import feedparser
import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
import os  # 운영체제 도구 추가

# 직접 쓰지 말고 시스템에서 가져오라고 시킵니다.
MY_KEY = os.environ.get('MY_KEY')
MY_EMAIL = os.environ.get('MY_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')

# 1. 설정
MY_KEY = "AIzaSyC6Zjt9xUYoR67zwRNEWgylRFOCffmY1LU"
MY_EMAIL = "sskiuyt@gmail.com"  # 보낼 사람 & 받을 사람 (본인 이메일)
APP_PASSWORD = "xuep cfla knmn lald" # 방금 발급받은 16자리 앱 비밀번호
MODEL_NAME = "models/gemini-2.5-flash-lite"

# 2. 뉴스 데이터 가져오기 (7개)
search_query = '(IT산업 OR "생성형 AI" OR "디지털 전환" OR "빅테크" OR "서비스 기획" OR "UX UI" OR "AI 활용")'
encoded_query = quote(search_query)
rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:1d&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(rss_url)
news_entries = feed.entries[:10]

    def get_ai_summary(title, snippet):
    url = f"https://generativelanguage.googleapis.com/v1/{MODEL_NAME}:generateContent?key={MY_KEY}"
    
    prompt = (
        f"뉴스 제목: {title}\n"
        f"내용 요약: {snippet}\n\n"
        "너는 IT 전문 큐레이터야. 위 뉴스 제목과 요약문을 보고, "
        "제목에 나오지 않은 구체적인 맥락이나 의미를 한 줄로 짧게 설명해줘."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return "요약 실패"

# 3. 이메일 발송 함수
def send_gmail(contents):
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = f"🚀 오늘의 IT 뉴스레터 ({time.strftime('%Y-%m-%d')})"

    body = "<h2>오늘의 IT 주요 뉴스 요약</h2><br>" + contents
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, APP_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("✅ 이메일 발송 성공!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

# 4. 메일 내용 구성 및 실행
full_content = ""
for i, entry in enumerate(news_entries):
    title = entry.title.split(' - ')[0]
    snippet = entry.summary.split('<')[0] if 'summary' in entry else ""
    summary = get_ai_summary(title, snippet)
    
    # 메일에 들어갈 HTML 형식 구성
    full_content += f"<b>{i+1}. {title}</b><br>"
    full_content += f"💡 핵심: {summary}<br>"
    full_content += f"🔗 <a href='{entry.link}'>기사 보기</a><br><br>"
    time.sleep(2)

if full_content:
    send_gmail(full_content)
