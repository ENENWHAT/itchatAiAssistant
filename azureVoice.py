import json

import requests
import time
import threading

token = ''
with open('config.json', 'r', encoding='utf-8') as f:
    configData = json.load(f)

tts_person = [
    {"gender": "Female", "shortName": "zh-CN-XiaoxiaoNeural", "chineseName": "晓晓"},
    {"gender": "Female", "shortName": "zh-CN-XiaoyiNeural", "chineseName": "小怡"},
    {"gender": "Female", "shortName": "zh-CN-XiaochenNeural", "chineseName": "小晨"},
    {"gender": "Female", "shortName": "zh-CN-XiaohanNeural", "chineseName": "小涵"},
    {"gender": "Female", "shortName": "zh-CN-XiaomengNeural", "chineseName": "小梦"},
    {"gender": "Female", "shortName": "zh-CN-XiaomoNeural", "chineseName": "小墨"},
    {"gender": "Female", "shortName": "zh-CN-XiaoqiuNeural", "chineseName": "小秋"},
    {"gender": "Female", "shortName": "zh-CN-XiaoruiNeural", "chineseName": "小蕊"},
    {"gender": "Female", "shortName": "zh-CN-XiaoshuangNeural", "chineseName": "小霜"},
    {"gender": "Female", "shortName": "zh-CN-XiaoxuanNeural", "chineseName": "小璇"},
    {"gender": "Female", "shortName": "zh-CN-XiaoyanNeural", "chineseName": "小妍"},
    {"gender": "Female", "shortName": "zh-CN-XiaoyouNeural", "chineseName": "小友"},
    {"gender": "Female", "shortName": "zh-CN-XiaozhenNeural", "chineseName": "小珍"},
    {"gender": "Female", "shortName": "zh-CN-XiaochenMultilingualNeural", "chineseName": "小晨（多语言）"},
    {"gender": "Female", "shortName": "zh-CN-XiaorouNeural", "chineseName": "小柔"},
    {"gender": "Female", "shortName": "zh-CN-XiaoxiaoDialectsNeural", "chineseName": "晓晓（方言）"},
    {"gender": "Female", "shortName": "zh-CN-XiaoxiaoMultilingualNeural", "chineseName": "晓晓（多语言）"},
    {"gender": "Male", "shortName": "zh-CN-YunxiNeural", "chineseName": "云希"},
    {"gender": "Male", "shortName": "zh-CN-YunjianNeural", "chineseName": "云剑"},
    {"gender": "Male", "shortName": "zh-CN-YunyangNeural", "chineseName": "云扬"},
    {"gender": "Male", "shortName": "zh-CN-YunfengNeural", "chineseName": "云峰"},
    {"gender": "Male", "shortName": "zh-CN-YunhaoNeural", "chineseName": "云浩"},
    {"gender": "Male", "shortName": "zh-CN-YunxiaNeural", "chineseName": "云霞"},
    {"gender": "Male", "shortName": "zh-CN-YunyeNeural", "chineseName": "云野"},
    {"gender": "Male", "shortName": "zh-CN-YunzeNeural", "chineseName": "云泽"},
    {"gender": "Male", "shortName": "zh-CN-YunjieNeural", "chineseName": "云杰"},
    {"gender": "Male", "shortName": "zh-CN-YunyiMultilingualNeural", "chineseName": "云逸（多语言）"}
]


def autoGetToken():
    global token
    while True:
        token = getToken()
        time.sleep(540)  # 9分钟，以秒为单位


def getToken():
    url = "https://" + configData['azureVoiceRegion'] + ".api.cognitive.microsoft.com/sts/v1.0/issueToken"
    payload = {}
    headers = {
        'Ocp-Apim-Subscription-Key': configData['azureVoiceKey'],
        'Host': configData['azureVoiceRegion'] + '.api.cognitive.microsoft.com',
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        print(e)
        return
    else:
        return response.text


def getPVoice(name):
    for i in tts_person:
        if i['chineseName'] == name:
            return {'gender': i['gender'], 'name': i['shortName']}


def getTts(gender, name, mind, word):
    url = "https://"+configData['azureVoiceRegion']+".tts.speech.microsoft.com/cognitiveservices/v1"

    payload = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' " \
              "xmlns:mstts='https://www.w3.org/2001/mstts'  xml:lang='zh-CN'><voice xml:lang='zh-CN' " \
              "xml:gender='" + gender + "'\r\n    name='" + name + "'><mstts:express-as style='" + mind + "' " \
                                                                                                          "styledegree='100'>\r\n" + word + "\r\n</mstts:express-as" \
                                                                                                                                            "></voice></speak> "
    headers = {
        'Authorization': 'Bearer ' + token,
        'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
        'User-Agent': 'hello',
        'Ocp-Apim-Subscription-Key': configData['azureVoiceKey'],
        'Content-Type': 'application/ssml+xml',
        'Accept': '*/*',
        'Host': configData['azureVoiceRegion'] + '.tts.speech.microsoft.com',
        'Connection': 'keep-alive'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))
    return response.content


threading.Thread(target=autoGetToken).start()
