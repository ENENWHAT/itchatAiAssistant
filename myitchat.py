import itchat
from itchat.content import *
import assistant
import os
from PIL import Image

friendDic = {}


# 添加一个定时任务 发送天气 以及 早报

@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING])
def handler_single_msg(msg):
    uName = msg['FromUserName']
    try:
        return dotheThing(msg)
    except Exception as e:
        e = str(e)
        print(e)
        assistant.exceptionOK(friendDic.get(uName))
        if 'Rate limit exceeded for images per minute' in e:
            return '一分钟最多处理5张图'
        return '发生网络错误，请重试！'


# 群内使用时的功能
@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING], isGroupChat=True)
def text_reply(msg):
    uName = msg['FromUserName']
    try:
        return dotheThing(msg)
    except Exception as e:
        e = str(e)
        print(e)
        assistant.exceptionOK(friendDic.get(uName))
        if 'Rate limit exceeded for images per minute' in e:
            return '一分钟最多处理5张图'
        return '发生网络错误，请重试！'


def dotheThing(msg):
    lst = itchat.get_msg()
    info = msg['Text']  # 取出消息内容
    msgId = msg['MsgId']  # 取出消息标识
    info_type = msg['Type']  # 取出消息类型
    name = msg['FileName']  # 取出消息文件名
    # 取出消息发送者标识并从好友列表中检索
    ttt = False
    print(info_type)
    print(name)
    print(info)
    print(msgId)
    uName = msg['FromUserName']
    print(uName)
    # fromUser = itchat.search_friends(userName=msg['FromUserName'])['NickName']
    if info_type == 'Recording':
        msg.download(name)
        info = assistant.transVoice(name)
        ttt = True
    if info_type == 'Picture':
        imgPath = uName + '上传图片.png'
        msg.download(imgPath)
        img = Image.open(imgPath)
        img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
        img.save(imgPath, 'PNG')
        img.close()
        ttt = True
        info = '我已经上传了一张图片，请不要提示请上传图片。可以询问我需要对这个图片做什么'
    if info_type == 'Text' or ttt:
        print(friendDic.get(uName))
        if friendDic.get(uName) is None:
            threadId = assistant.add_thread()
            assistant.userDic[threadId] = uName
            friendDic[uName] = threadId
            s = assistant.send_message(info, threadId)
        else:
            s = assistant.send_message(info, friendDic.get(uName))
        print(s)
        if s['type'] == 'file':
            sendFile(s['name'], uName, s['content'])
        elif s['type'] == 'failed':
            return '回答失败，重新提问'
        elif s['type'] == 'null':
            return None
        else:
            return s['content']


def sendFile(filename, uName, content):
    filename = filename
    with open(filename, 'wb') as f:
        f.write(content)
    print(uName)
    itchat.send_file(filename, uName)
    os.remove(filename)
    print("发送完成")


def sendImage(filename, uName, content):
    filename = uName + filename
    with open(filename, 'wb') as f:
        f.write(content)
    print(uName)
    itchat.send_image(filename, uName)
    # os.remove(filename)
    print("发送完成")


def sendMsg(content, uName):
    print(content)
    print(uName)
    itchat.send_msg(content, uName)


assistant.sendF = sendFile
assistant.sendM = sendMsg
assistant.sendI = sendImage

itchat.auto_login(hotReload=False, enableCmdQR=2)
friends = itchat.get_friends(update=True)
friendsList = []
for i in friends:
    if i['RemarkName']:
        friendsList.append({'RemarkName': i['RemarkName'], 'UserName': i['UserName']})
for i in friendsList:
    print(i)
assistant.update_friend(friendsList)

itchat.run()
input("按下 Enter 键退出...")
