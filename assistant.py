import base64
import json
import os
import threading
import time
import requests
import azureVoice
from openai import OpenAI

with open('config.json', 'r', encoding='utf-8') as f:
    configData = json.load(f)
client = OpenAI(api_key=configData['openAIKey'], base_url=configData['baseUrl'] + "/v1")

sendF = ''
sendM = ''
sendI = ''
friendList = []
currentRunId = ''
userDic = {}
curVoice = {'gender': 'Female', 'name': 'zh-CN-XiaoyiNeural'}
userVoice = {}
assistant = ''
tools = [{"type": "code_interpreter"}]

with open('myTools.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
tools = tools + data['tools']
theadDic = {}


def setAssistant():
    while len(friendList) == 0:
        time.sleep(0.2)
    remarkNameList = []
    for ii in friendList:
        remarkNameList.append(ii['RemarkName'])
    for i in tools[1:]:
        print(i)
        if i['function']['name'] == 'sendToFriend':
            i['function']['parameters']['properties']['name']['enum'] = remarkNameList
            print(i)
            break
    print(friendList)
    global assistant
    assistant = client.beta.assistants.create(
        name='安雅',
        instructions="你是微信小助手，安雅,尽量模拟一个知性小秘书的口吻去回复问题。说话，回复内容尽量简短一点",
        description='你是美丽性感聪明的安雅大美女，用中文回答问题',
        model=configData['model'],  # gpt-4-1106-preview  或  gpt-3.5-turbo-1106
        tools=tools,
    )


threading.Thread(target=setAssistant).start()


def add_thread():
    thread = client.beta.threads.create()
    theadDic[thread.id] = True
    userVoice[thread.id] = curVoice
    return thread.id


def send_message(message, theadid):
    if not theadDic[theadid]:
        time.sleep(0.5)
        send_message(message, theadid)
    theadDic[theadid] = False

    message = client.beta.threads.messages.create(
        thread_id=theadid,
        role="user",
        content=message
    )
    run = client.beta.threads.runs.create(
        thread_id=theadid,
        assistant_id=assistant.id,
    )

    # 每0.5秒执行一次 run完后返回
    ts = 0
    while True:
        if ts > 300:
            exceptionOK(theadid)
            print("生成超时了")
            return {'type': 'failed'}
        run = client.beta.threads.runs.retrieve(  # 通过thread.id和run.id来查看run的状态
            thread_id=theadid,
            run_id=run.id
        )
        global currentRunId
        currentRunId = run.id
        print(run.status)
        if run.status not in ['in_progress', 'failed', 'requires_action', 'queued']:
            result = {}
            messages = client.beta.threads.messages.list(thread_id=theadid)
            res = messages.data[0].content[0]
            # print(messages)
            # print(res)
            if res.text.annotations:
                resf = res.text.annotations[0].file_path.file_id
                response = client.files.content(resf)
                if response:
                    print(response)
                    print(response.content)
                    result['content'] = response.content
                result['type'] = 'file'
                print(res)
                result['name'] = res.text.annotations[0].text.split("/")[-1]
                print(result)
            else:
                result['type'] = 'word'
                result['content'] = messages.data[0].content[0].text.value

            theadDic[theadid] = True  # 为True表示空闲
            return result
        elif run.status == 'failed':
            theadDic[theadid] = True
            return {'type': 'failed'}
        elif run.status == 'requires_action':
            calls = run.required_action.submit_tool_outputs.tool_calls
            print(calls)
            outputs = []
            for fun in calls:
                myfun = globals()[fun.function.name]
                arguments = fun.function.arguments
                arguments = json.loads(arguments)
                rs = myfun(**arguments)
                if rs[:7] == '声音%$@回复':
                    mw = json.loads(rs[7:])
                    res = azureVoice.getTts(userVoice[theadid]['gender'], userVoice[theadid]['name'], mw['mind'],
                                            mw['word'])
                    sendF('语音.wav', userDic[theadid], res)
                    rs = '{"voice":"OK"}'
                elif rs[:5] == '查%$@询':
                    print("查询")
                    sendM(rs[5:12], userDic[theadid])
                    rs = rs[12:]
                elif rs[:7] == '图片%$@生成':
                    print("正在生成")
                    res = gen_pic_do(rs[7:])
                    sendI('上传图片.png', userDic[theadid], res)
                    print('完成')
                    rs = '只返回生成完成，不说多余话'
                elif rs[:7] == '图片%$@ps':
                    print("正在生成")
                    jsonIn = rs[7:]
                    jsonIn = json.loads(jsonIn)
                    res = edit_pic_do(jsonIn['prompt'], jsonIn['mask'], userDic[theadid])
                    sendI('上传图片.png', userDic[theadid], res)
                    print('完成')
                    rs = '只返回生成完成，不说多余话'
                elif rs[:7] == '图片%$@转化':
                    res = trans_pic_do(userDic[theadid])
                    rs = '只返回生成完成，不说多余话'
                    sendI('上传图片.png', userDic[theadid], res)
                elif rs[:7] == '图片%$@识别':
                    res = vision_do(userDic[theadid], rs[7:])
                    rs = res
                elif rs[:5] == '改%$@声':
                    userVoice[theadid] = azureVoice.getPVoice(rs[5:])

                outputs.append({'tool_call_id': fun.id, 'output': rs})
            if len(outputs) == 0:
                client.beta.threads.runs.cancel(run_id=run.id, thread_id=theadid)
                theadDic[theadid] = True

                return {'type': 'null'}

            else:
                client.beta.threads.runs.submit_tool_outputs(run_id=run.id, thread_id=theadid, tool_outputs=outputs)
        # 继续请求
        time.sleep(0.5)
        ts = ts + 0.5


def exceptionOK(theadid):
    if currentRunId == "":
        theadDic[theadid] = True
        return
    try:
        client.beta.threads.runs.cancel(run_id=currentRunId, thread_id=theadid)
        theadDic[theadid] = True
    except Exception as e:
        print("关闭" + theadid + "错误")
        print(str(e))


# 语音识别
def transVoice(fileName):
    audio_file = open(fileName, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcript.text)
    return transcript.text


def get_weather():
    return "查%$@询点击#查看天气完成"


def answer_with_voice(mind, word):
    return '声音%$@回复' + json.dumps({'mind': mind, 'word': word})


def change_voice(name):
    return '改%$@声' + name


def get_Calender():
    return "查%$@询点击#查看日历只返回操作成功，不说多余的话,不询问"


# 汇率 快递
def get_hl():
    return "查%$@询点击#查看汇率只返回操作成功，不说多余的话,不询问"


def get_kd():
    return "查%$@询点击#查看快递只返回操作成功，不说多余的话,不询问"


def get_weibo_realTimeHot():
    return "https://s.weibo.com/top/summary?cate=realtimehot"


def get_maoYan_rank():
    return 'https://piaofang.maoyan.com/box-office?ver=normal'


def gen_pic(prompt):
    return '图片%$@生成' + prompt


def edit_pic(prompt, mask):
    return '图片%$@ps' + json.dumps({'prompt': prompt, 'mask': mask})


def trans_pic():
    return '图片%$@转化'


def vision(prompt):
    return '图片%$@识别' + prompt


# 生成图
def gen_pic_do(prompt):
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print(response.data)
    image_url = response.data[0].url
    res = requests.get(image_url)
    return res.content


# 图片根据mask修改mask区域
def edit_pic_do(prompt, mask, uName):
    img = uName + '上传图片.png'
    if not os.path.exists(img):
        return None
    response = client.images.edit(
        model="dall-e-2",
        image=open(img, "rb"),
        mask=open("masks/" + mask + ".png", "rb"),
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    print(response.data)
    image_url = response.data[0].url
    res = requests.get(image_url)
    return res.content


# 图片变换、重新生成、微调、vision
def trans_pic_do(uName):
    img = uName + '上传图片.png'
    response = client.images.create_variation(
        image=open(img, "rb"),
        n=2,
        size="1024x1024"
    )
    image_url = response.data[0].url
    res = requests.get(image_url)
    return res.content


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def update_friend(friends):
    global friendList
    friendList = friends


# 给好友发送消息
def sendToFriend(word, name, minutes):
    for i in friendList:
        if i['RemarkName'] == name:
            threading.Timer(minutes * 60, sendM, args=(word, i['UserName'])).start()
            break
    return "完成"


# 图片vision
def vision_do(uName, prompt):
    img = uName + '上传图片.png'
    # Function to encode the image
    imgBase64 = encode_image(img)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imgBase64}",
                        },
                    }
                ],
            }
        ],
        max_tokens=300,
    )
    p = response.choices[0]
    print(p.message.content)
    return p.message.content
