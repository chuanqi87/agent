<template>
  <div class="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- 状态栏 -->
    <div class="bg-white shadow-sm border-b px-6 py-2">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center">
          <span class="text-blue-600 mr-2">🤖</span>
          AI Agent 助手
        </h2>
        <div class="flex items-center space-x-2">
          <div 
            :class="[
              'w-3 h-3 rounded-full',
              apiStore.isConnected ? 'bg-green-500' : 'bg-red-500'
            ]"
          ></div>
          <span class="text-sm text-gray-600">
            {{ apiStore.isConnected ? '已连接' : '未连接' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <main class="flex-1 overflow-hidden">
      <div 
        class="h-full overflow-y-auto px-6 py-4 space-y-4"
        ref="chatContainer"
      >
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4">👋</div>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">欢迎使用 AI Agent 助手</h2>
          <p class="text-gray-500">请输入您的问题，我会尽力为您提供帮助</p>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="[
            'flex',
            message.type === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div 
            :class="[
              'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
              message.type === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-white text-gray-800 shadow-sm'
            ]"
          >
            <!-- 用户消息 -->
            <p v-if="message.type === 'user'" class="text-sm">{{ message.content }}</p>
            <!-- AI消息 - 支持markdown -->
            <div 
              v-else
              class="text-sm markdown-content"
              v-html="renderMarkdown(message.content)"
            ></div>
            <span class="text-xs opacity-70 mt-1 block">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
        </div>

        <!-- 思考状态 -->
        <div v-if="apiStore.isThinking" class="flex justify-start">
          <div class="bg-white text-gray-800 shadow-sm max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
            <div class="flex items-center space-x-2">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
              <span class="text-sm">AI正在思考中...</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="bg-white border-t px-6 py-4">
      <div class="flex space-x-4">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          :disabled="!apiStore.isConnected || apiStore.isThinking"
          type="text"
          placeholder="输入您的问题..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          @click="sendMessage"
          :disabled="!apiStore.isConnected || apiStore.isThinking || !inputMessage.trim()"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          发送
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useApiStore } from '../stores/api'
import { renderMarkdown } from '../utils/markdown'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const apiStore = useApiStore()
const { connect, disconnect, sendMessageStream } = apiStore

const messages = ref<Message[]>([])
const inputMessage = ref('')
const chatContainer = ref<HTMLElement>()

// 计算对话历史，用于发送给API
const conversationHistory = computed((): ChatMessage[] => {
  return messages.value.map(msg => ({
    role: msg.type === 'user' ? 'user' : 'assistant',
    content: msg.content
  }))
})

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || !apiStore.isConnected || apiStore.isThinking) return

  // 添加用户消息
  const userMessage: Message = {
    id: Date.now().toString(),
    type: 'user',
    content: message,
    timestamp: new Date()
  }
  messages.value.push(userMessage)

  // 清空输入
  inputMessage.value = ''
  
  // 滚动到底部
  scrollToBottom()

  // 创建AI消息占位符
  const aiMessage: Message = {
    id: (Date.now() + 1).toString(),
    type: 'ai',
    content: '',
    timestamp: new Date()
  }
  messages.value.push(aiMessage)
  scrollToBottom()

  // 使用SSE流式接收回复
  sendMessageStream(
    message,
    conversationHistory.value.slice(0, -2), // 排除刚添加的用户消息和AI占位符
    // onChunk: 每次收到内容片段时调用
    (chunk: string) => {
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.type === 'ai') {
        lastMessage.content += chunk
        scrollToBottom()
      }
    },
    // onComplete: 流式完成时调用
    () => {
      scrollToBottom()
    },
    // onError: 出错时调用
    (error: string) => {
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.type === 'ai') {
        lastMessage.content = `错误: ${error}`
      }
      scrollToBottom()
    }
  )
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

onMounted(async () => {
  await connect()
})

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
/* 组件特定样式 */

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-weight: bold;
  margin: 0.8em 0 0.4em 0;
}

.markdown-content :deep(h1) { font-size: 1.5em; }
.markdown-content :deep(h2) { font-size: 1.3em; }
.markdown-content :deep(h3) { font-size: 1.1em; }

.markdown-content :deep(p) {
  margin: 0.5em 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.5em 0 0.5em 1.2em;
}

.markdown-content :deep(li) {
  margin: 0.2em 0;
}

.markdown-content :deep(code) {
  background-color: #f1f5f9;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 1em;
  margin: 0.8em 0;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.85em;
  line-height: 1.4;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #e2e8f0;
  padding-left: 1em;
  margin: 0.8em 0;
  color: #64748b;
  font-style: italic;
}

.markdown-content :deep(strong) {
  font-weight: bold;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 0.4em 0.8em;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f8fafc;
  font-weight: bold;
}
</style> 