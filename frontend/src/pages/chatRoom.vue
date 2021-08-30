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
