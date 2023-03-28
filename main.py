TOKEN = OPENAI_API_KEY
import os
import openai
import requests
import json
import time
import sys
import yt_dlp
from pydub import AudioSegment

# 設定 yt_dlp 下載影片的選項
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'joeman',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
yturl = input("請輸入貼上YT的影片連結: ")
# 填入影片的 URL
url = yturl

# 建立 yt_dlp 下載器物件並下載音檔
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

# 載入 MP3 音檔
sound = AudioSegment.from_file('joeman.mp3', format='mp3')

# 設定每個分割檔案的長度（單位：毫秒）
segment_length = 1000000

transcripts = []
# 將音檔分割成多個檔案
for i, chunk in enumerate(sound[::segment_length]):
    # 設定分割檔案的檔名
    chunk.export(f'output_{i}.mp3', format='mp3')
print(f'音檔總共分割{i+1}份')
print()
print(f'開始將{i+1}份音檔交給WhisperAI製作語音辨識轉錄稿')
print()
openai.api_key = TOKEN
# 使用 OpenAI API 轉換音檔為文字
for o in range(i+1):
    audio_file = open(f'output_{o}.mp3', "rb")
    transcript_i = openai.Audio.transcribe("whisper-1", audio_file)
    print(f'已完成第{o+1}份音檔AI語音辨識')
    transcripts.append(transcript_i.text)
print()
print(f'開始將{i+1}份AI語音辨識轉錄稿轉交給ChatGPT作影片摘要')
# 將所有文字合併
my_ret = '  '.join(transcripts)

# 使用 ChatGPT API 摘要文章
transcript_ary = []
ret = ''
for script in my_ret.split():
    ret = ret + ' ' + script
    if len(ret) > 1500:
        transcript_ary.append(ret)
        ret = ''
transcript_ary.append(ret)

result_ary = []
for t in transcript_ary:
    print()
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "請你成為YT影片摘要的小幫手，以下為轉錄稿部分內容，有可能是影片開頭，有可能是中間部分，有可能是結尾部分，以繁體中文輸出。"},
        {"role": "user", "content": t}
        ],
        stream=True
    )
    hs = []
    for r in completion:
        for choice in r.choices:
            message = choice.delta.get('content', '')
            if message:
                sys.stdout.write(f"{message}")                                        
                sys.stdout.flush()
                hs.append(message) 
    mshs_data = ''.join(hs)
    result_ary.append(mshs_data)
    print()

# 輸出摘要結果
# for res in result_ary:
    # print()
    # print(res.get('content'))
