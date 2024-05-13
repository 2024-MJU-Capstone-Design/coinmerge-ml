import os
#!/usr/bin/env python3
#-*- codig: utf-8 -*-
import sys
import requests
import json
import psycopg2.extras
import openai
# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()
db = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="postgres", port=5432)
cursor=db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
file_path="./datas/news_tuning.jsonl"
openai_client = openai.OpenAI(api_key=os.environ.get("API_KEY"))

def get_allnews():
    cursor.execute("SELECT * FROM public.news")
    result = cursor.fetchall()
    print(result)
    return result

def summarize_allnews(allnews):
    client_id = "jospmk76t8"
    client_secret = "6eKmYbwsitbJN08xmQgqbpiJEseuIvCz0v5UFZGJ"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }
    language = "ko"  # Language of document (ko, ja )
    model = "news"  # Model used for summaries (general, news)
    tone = "2"  # Converts the tone of the summarized result. (0, 1, 2, 3)
    summaryCount = "3"  # This is the number of sentences for the summarized document.
    url = "https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize"

    for news in allnews:
        results = {
            "messages": [],
        }
        print(news)
        data = {
            "document": {
                "title": news["title"],
                "content": news["content"]
            },
            "option": {
                "language": language,
                "model": model,
                "tone": tone,
                "summaryCount": summaryCount
            }
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(response.text)
        rescode = response.status_code
        token = "비트코인"
        response_json = json.loads(response.text)
        if (rescode == 200):
            results.get("messages").append({"role": "assistant", "content": token+"과 관련된 뉴스야." + "뉴스 내용은 " + response_json["summary"]})
            with open(file_path, "a") as f:
                json.dump(results, f, ensure_ascii=False)
                f.write("\n")
        else:
            print("Error : " + response.text)

def fine_tuning_news():
    file_upload_result = openai_client.files.create(file=open(file_path, "rb"), purpose="fine-tune")
    tuning_complete_result=openai_client.fine_tuning.jobs.create(training_file=file_upload_result.id, model="gpt-3.5-turbo")
    print(tuning_complete_result)


# allnews = get_allnews()
# summarize_allnews(allnews)
fine_tuning_news()