# @Time    : 2021/8/21 17:41
# @Author  : fanlu
from flask import Flask, render_template
from flask_socketio import SocketIO,emit,send
from flask_cors import *

app = Flask(__name__)
CORS(app,supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

onlineUserSum = 0
usernamelist = []


# 连接事件
@socketio.on('connect',namespace="/chat")
def connect():
    print("连接成功")
    global onlineUserSum
    onlineUserSum +=1
    emit('onlineUsernameList',usernamelist)
    emit('usercount',{'count':onlineUserSum},broadcast=True)


# 断开连接事件
@socketio.on('disconnect',namespace="/chat")
def disconnect():
    print("断开连接")
    global onlineUserSum
    onlineUserSum-=1
    emit('usercount',{'count':onlineUserSum},broadcast=True)


# 移除用户名
@socketio.on('removeUsername',namespace="/chat")
def removeUsername(delname):
    global usernamelist
    if(delname['username'] in usernamelist):
        usernamelist.remove(delname['username'])
        emit('onlineUsernameList',{'list':usernamelist},broadcast=True)

# 收到新消息进行转发
@socketio.on('newmessage',namespace="/chat")
def new_message(message_body):
    print("收到新消息:",message_body)
    emit('newmessage',{'username':message_body['username'],'msg':message_body['msg']},broadcast=True)


# 验证用户名是否可用
@socketio.on('verifyUsername',namespace="/chat")
def verifyUsername(unverify):
    print("设置用户名",unverify)
    global usernamelist
    if(unverify['username'] not in usernamelist):
        usernamelist.append(unverify['username'])
        emit('checkUsername',{'isOK':True})
        emit('onlineUsernameList',{'list':usernamelist},broadcast=True)
    else:
        emit('checkUsername',{'isOK':False})


@app.route("/socket.io",methods=["POST","GET"])
def HeartBeat():
    print('监听客户端消息')
    return "心跳"


# 必须啊安装 eventlet 或者 gevent
# 前端必须使用socketio!!!!!!!!!!!! 否则报404错误
if __name__ == '__main__':
    socketio.run(app,debug=True,host='localhost',port=5000)













