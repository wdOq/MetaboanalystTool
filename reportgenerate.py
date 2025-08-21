import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv("forllm.env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def analyze_image_with_llm(image_path, prompt):
    try:
        print("開始讀取圖片...")
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        print("圖片編碼完成，開始呼叫 API...")
        prompt = f"""
                        You're a metabolomics assistant. Please analyze the output data I send you and you have to explain the basic knowledge in report.For example, you have to explain what is the meaning of p-value. At what level is this value consider relevant.The output data I send you is a result from MetaboAnalyst which is a web-based platform dedicated for comprehensive metabolomics data analysis, interpretation and integration with other omics data. The picture include the analysis of fold change,T-test and Anova. I want the analysis in bullet point and do not use asterisks (*). Use numbered format like 1., 2., 3., etc..
                """
        payload = {
            "model": "google/gemma-3-27b-it:free", 
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=60)
        print(f"API 回應狀態碼：{response.status_code}")
        response.raise_for_status()
        result = response.json()
        print("API 回應取得成功")
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "reportgenerate.py Error: Request timed out. Please try again later."
    except requests.exceptions.HTTPError as e:
        return f"reportgenerater.py錯誤 HTTP Error:  {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"reportgenerater.py錯誤: {str(e)}"
