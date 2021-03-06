# flask+vue+socketio极简聊天室

## websocket介绍

在 WebSocket API 中，浏览器和服务器只需要做一个握手的动作，然后，浏览器和服务器之间就形成了一条快速通道。两者之间就直接可以数据互相传送。

### 事件

| 事件    | 事件处理程序     | 描述                       |
| :------ | :--------------- | :------------------------- |
| open    | Socket.onopen    | 连接建立时触发             |
| message | Socket.onmessage | 客户端接收服务端数据时触发 |
| error   | Socket.onerror   | 通信发生错误时触发         |
| close   | Socket.onclose   | 连接关闭时触发             |

### 方法

| 方法           | 描述             |
| :------------- | :--------------- |
| Socket.send()  | 使用连接发送数据 |
| Socket.close() | 关闭连接         |

## socketio介绍

Socket.io 是一个完全由 JavaScript 实现、基于 Node.js、支持 WebSocket 协议的用于实时通信、跨平台的开源框架，它包括了客户端的 JavaScript 和服务器端的 Node.js。

Socket.io 设计的目标是支持任何的浏览器，任何 Mobile 设备。支持主流的 PC 浏览器 (IE,Safari,Chrome,Firefox,Opera等)，Mobile 浏览器(iphone Safari/ipad Safari/Android WebKit/WebOS WebKit等)。

但是，WebSocket 协议是 HTML5 新推出的协议，浏览器对它的支持并不完善，由此可以看出，Socket.io 不可能仅仅是对 WebSocket 的实现，它还支持其他的通信方式，如上面介绍过的 ajax 轮询和 Long Polling。根据浏览器的支持程度，自主选择使用哪种方式进行通讯。

## flask后端实现

### flask - socketio

**Flask-SocketIO** 使 Flask 应用程序能够访问客户端和服务器之间的低延迟双向通信。客户端应用程序可以使用 Javascript，C ++，Java 和 Swift 中的任何 [SocketIO](https://link.zhihu.com/?target=http%3A//socket.io/) 官方客户端库或任何兼容的客户端来建立与服务器的永久连接。

安装:

```python3
pip install flask-socketio
```

### 部分使用方法

- 命名空间

  ```python
  @socketio.on('connect', namespace='/test')
  ```

- 自定义事件

  ```python
  @socketio.on('my event')
  def handle_my_custom_event(json):
  ```

- 无名事件
  send方法: 由客户端的onmessage方法接收

- 命名事件
  emit方法: 由客户端的注册命名方法接收

- 广播

  ```python
  emit('my response', data, broadcast=True)
  ```

- 自带join_room 和leave_room方法

- 异常处理

  ```python
  @socketio.on_error()        # Handles the default namespace
  def error_handler(e):
      pass
  
  @socketio.on_error('/chat') # handles the '/chat' namespace
  def error_handler_chat(e):
      pass
  
  @socketio.on_error_default  # handles all namespaces without an explicit error handler
  def default_error_handler(e):
      pass
  ```

- **必须安装eventlet 或者gevent来支持异步请求!!!!!!!!!!!!!!**

### 聊天室服务端实现(单一聊天室)

> 主要包括几个功能:
>
> 1. 进入聊天室, 通知每个客户端人数加1
> 2. 断开连接事件, 通知每个客户端人数减1
> 3. 用户设置用户名: 检查并给出反馈
> 4. 转发用户新消息给所有客户端
> 5. 心跳连接
>
> **使用版本4.3.1  版本很可能会造成问题!!!!!!!!**

具体代码:

```python
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
```

## vue前端实现

### 前端基础项目

https://github.com/FanLu1994/vue2-elementui-tailwind-template

### 安装vue-socketio 2.1.0版本

npm install vue-socketio@2.1.0

### 配置vue-socketio

```js
// main.js
import VueSocketIO from "vue-socket.io";

Vue.use(VueSocketIO,'http://127.0.0.1:5000/chat')
```

### 新建页面

src/pages/chatRoom.vue

```vue
<template>
  <div class="container mx-auto bg-green-200 py-10 h-screen grid grid-cols-4 rounded-2xl shadow-md">
    <div class="flex flex-col text-left ml-4">
      <div>当前在线人数：{{onlineUserSum}}</div>
      <div>用户列表：
        <br>
        <p v-for="username in onlineUsernameList.list" :key="username">{{username}}</p>
      </div>
    </div>

    <div class="w-9/12 mx-auto my-3  pl-0 col-span-3  flex flex-col">
      <div class="bg-white h-64 mb-2 overflow-auto rounded px-5" id="messageBox">
        <p v-for="(message,index) in historyMessage" :key="index" class="text-left" :class="[username===message.username? 'text-red-500':'']">
          {{message.username}} 说：
          {{message.msg}}
          <br>
          ---------------------
        </p>
      </div>
      <div class="grid grid-cols-2 space-x-2 mx-auto w-3/4">
        <el-input  type="textarea" v-model="message" placeholder="请输入内容"  @keyup.enter.native="sendMessage()" ></el-input>
        <el-button  @click="sendMessage()" >发送</el-button>
      </div>
    </div>

<!--    <el-input v-model="username"  :disabled="usernameOK"  placeholder="请输入用户名"></el-input>-->
    <el-dialog
      title="设置用户名"
      :visible.sync="dialogVisible"
      custom-class="round shadow-lg"
      width="15%">
      <div>
        <el-input placeholder="请输入用户名" v-model="username"></el-input>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="setUsername">确 定</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import VueSocketIO from "vue-socket.io";
import store from "../store/store";
import axios from "axios";

export default {
  name: "chatRoom",
  data(){
    return {
      historyMessage : [],
      message:'',
      username:'',
      onlineUserSum:'',
      onlineUsernameList:[],
      usernameOK:false,

      dialogVisible:false,
    }
  },

  created() {
    window.addEventListener('beforeunload', e => this.beforeunloadFn(e))
  },

  mounted() {
    this.$socket.open()
  },

  destroyed() {
    window.removeEventListener('beforeunload', e => this.beforeunloadFn(e))
  },

  methods:{
    // 发送消息
    sendMessage(){
      if(this.username===''){
        this.dialogVisible = true
        return
      }

      this.$socket.emit('newmessage',{username:this.username,msg:this.message})
      console.log("发送完毕")
      this.message = ''
    },

    // 删除用户
    beforeunloadFn(){
      this.$socket.emit("disconnect")
      if(this.username!==''){
        this.$socket.emit('removeUsername')
      }
    },

    // 设置用户名
    setUsername(){
      this.$socket.emit("verifyUsername",{username:this.username})
    }

  },

  sockets: {
    connect() {
      console.log('socket connected')
    },
    // 链接失败
    disconnect() {
      console.log('socket disconnect')
    },
    // 重新连接
    reconnect() {
      console.log('socket reconnect')
    },

    newmessage:function(getMessage){
      this.historyMessage.push(getMessage)
      let messageBox = document.getElementById('messageBox');
      messageBox.scrollTop = messageBox.scrollHeight+10;

    },
    usercount:function(Sum){
      this.onlineUserSum = Sum.count
    },
    checkUsername:function(result){
      console.log(result)
      if(result.isOK === false){
        this.$message.error('用户名已被占用');
      }
      else{
        this.usernameOK = true
        this.dialogVisible = false
      }
    },
    onlineUsernameList:function(list){
      this.onlineUsernameList = list
    },
  }

}
</script>

<style scoped>

</style>

```

### 修改路由

```js
export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: ()=>import('../pages/chatRoom.vue'),
      meta:{title:'聊天室'}
    }
  ]
})
```



## 测试

### 启动后端:

python main.py

### 启动前端:

npm run dev

然后就可以在浏览器看到聊天室页面啦

