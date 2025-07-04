<template>
  <div class="flex flex-col h-screen bg-gradient-to-br from-purple-50 to-pink-100">
    <!-- 状态栏 -->
    <div class="bg-white shadow-sm border-b px-6 py-2">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center">
          <span class="text-purple-600 mr-2">🔧</span>
          Function Calling 演示
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

    <!-- 主要内容 -->
    <main class="flex-1 overflow-hidden flex">
      <!-- 左侧：工具配置 -->
      <div class="w-1/3 bg-white border-r p-6 overflow-y-auto">
        <h2 class="text-lg font-semibold mb-4">可用工具</h2>
        
        <!-- 天气工具 -->
        <div class="border rounded-lg p-4 mb-4">
          <div class="flex items-center mb-2">
            <input 
              type="checkbox" 
              id="weather-tool" 
              v-model="enabledTools.weather"
              class="mr-2"
            >
            <label for="weather-tool" class="font-medium">🌤️ 天气查询</label>
          </div>
          <p class="text-sm text-gray-600 mb-2">获取指定城市的天气信息</p>
          <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
            get_weather(city: string, unit?: string)
          </div>
        </div>

        <!-- 计算器工具 -->
        <div class="border rounded-lg p-4 mb-4">
          <div class="flex items-center mb-2">
            <input 
              type="checkbox" 
              id="calculator-tool" 
              v-model="enabledTools.calculator"
              class="mr-2"
            >
            <label for="calculator-tool" class="font-medium">🧮 计算器</label>
          </div>
          <p class="text-sm text-gray-600 mb-2">执行数学计算</p>
          <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
            calculate(expression: string)
          </div>
        </div>

        <!-- 时间工具 -->
        <div class="border rounded-lg p-4 mb-4">
          <div class="flex items-center mb-2">
            <input 
              type="checkbox" 
              id="time-tool" 
              v-model="enabledTools.time"
              class="mr-2"
            >
            <label for="time-tool" class="font-medium">⏰ 时间查询</label>
          </div>
          <p class="text-sm text-gray-600 mb-2">获取当前时间或时区信息</p>
          <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded font-mono">
            get_time(timezone?: string)
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区域 -->
      <div class="flex-1 flex flex-col">
        <!-- 聊天消息 -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="chatContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="text-6xl mb-4">🔧</div>
            <h2 class="text-xl font-semibold text-gray-700 mb-2">Function Calling 演示</h2>
            <p class="text-gray-500">启用工具函数后，AI可以调用这些函数来帮助您</p>
            <div class="mt-4 text-sm text-gray-400">
              <p>示例问题：</p>
              <ul class="list-disc list-inside mt-2 space-y-1">
                <li>"北京今天天气怎么样？"</li>
                <li>"计算 15 * 8 + 23"</li>
                <li>"现在几点了？"</li>
              </ul>
            </div>
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
                  ? 'bg-purple-500 text-white' 
                  : 'bg-white text-gray-800 shadow-sm'
              ]"
            >
              <!-- 用户消息 -->
              <div v-if="message.type === 'user'">
                <p class="text-sm">{{ message.content }}</p>
              </div>
              
              <!-- AI消息 -->
              <div v-else>
                <!-- 函数调用显示 -->
                <div v-if="message.toolCalls && message.toolCalls.length > 0" class="mb-2">
                  <div class="text-xs text-gray-500 mb-1">🔧 函数调用:</div>
                  <div 
                    v-for="toolCall in message.toolCalls" 
                    :key="toolCall.id"
                    class="bg-blue-50 p-2 rounded text-xs mb-1"
                  >
                    <div class="font-medium text-blue-700">{{ toolCall.function.name }}</div>
                    <div class="text-gray-600">{{ toolCall.function.arguments }}</div>
                  </div>
                </div>
                
                <!-- AI回复内容 -->
                <div 
                  v-if="message.content"
                  class="text-sm markdown-content"
                  v-html="renderMarkdown(message.content)"
                ></div>
              </div>
              
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
                <span class="text-sm">AI正在处理中...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <footer class="bg-white border-t px-6 py-4">
          <div class="flex space-x-4">
            <input
              v-model="inputMessage"
              @keyup.enter="sendMessage"
              :disabled="!apiStore.isConnected || apiStore.isThinking"
              type="text"
              placeholder="输入您的问题..."
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              @click="sendMessage"
              :disabled="!apiStore.isConnected || apiStore.isThinking || !inputMessage.trim()"
              class="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              发送
            </button>
          </div>
          
          <!-- 启用的工具数量显示 -->
          <div class="mt-2 text-xs text-gray-500">
            已启用 {{ enabledToolsCount }} 个工具
          </div>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useApiStore } from '../stores/api'
import { renderMarkdown } from '../utils/markdown'

interface Message {
  id: string
  type: 'user' | 'ai'
  content?: string
  toolCalls?: any[]
  toolResults?: Array<{
    tool_call_id: string
    content: string
  }>
  timestamp: Date
}

const apiStore = useApiStore()
const { connect, disconnect, sendMessageWithTools } = apiStore

const messages = ref<Message[]>([])
const inputMessage = ref('')
const chatContainer = ref<HTMLElement>()

// 工具启用状态
const enabledTools = ref({
  weather: true,
  calculator: true,
  time: true
})

// 计算启用的工具数量
const enabledToolsCount = computed(() => {
  return Object.values(enabledTools.value).filter(Boolean).length
})

// 构建工具列表
const buildTools = () => {
  const tools = []
  
  if (enabledTools.value.weather) {
    tools.push({
      type: "function",
      function: {
        name: "get_weather",
        description: "获取指定城市的天气信息",
        parameters: {
          type: "object",
          properties: {
            city: {
              type: "string",
              description: "城市名称，例如：北京、上海"
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"],
              description: "温度单位，默认摄氏度"
            }
          },
          required: ["city"]
        }
      }
    })
  }
  
  if (enabledTools.value.calculator) {
    tools.push({
      type: "function",
      function: {
        name: "calculate",
        description: "执行数学计算",
        parameters: {
          type: "object",
          properties: {
            expression: {
              type: "string",
              description: "要计算的数学表达式，例如：2+3*4"
            }
          },
          required: ["expression"]
        }
      }
    })
  }
  
  if (enabledTools.value.time) {
    tools.push({
      type: "function",
      function: {
        name: "get_time",
        description: "获取当前时间或指定时区的时间",
        parameters: {
          type: "object",
          properties: {
            timezone: {
              type: "string",
              description: "时区名称，例如：Asia/Shanghai, America/New_York"
            }
          }
        }
      }
    })
  }
  
  return tools
}

// 工具执行函数
const executeToolCall = async (toolCall: any): Promise<string> => {
  const { name, arguments: args } = toolCall.function
  
  try {
    const parsedArgs = JSON.parse(args)
    
    switch (name) {
      case 'get_weather':
        return await executeWeatherTool(parsedArgs)
      case 'calculate':
        return await executeCalculatorTool(parsedArgs)
      case 'get_time':
        return await executeTimeTool(parsedArgs)
      default:
        return `未知工具: ${name}`
    }
  } catch (error) {
    return `工具执行错误: ${error instanceof Error ? error.message : '未知错误'}`
  }
}

// 天气工具执行
const executeWeatherTool = async (args: { city: string, unit?: string }): Promise<string> => {
  const { city, unit = 'celsius' } = args
  
  // 模拟天气API调用
  const weatherData = {
    '北京': { temp: 15, desc: '晴天', humidity: 45 },
    '上海': { temp: 18, desc: '多云', humidity: 60 },
    '广州': { temp: 25, desc: '小雨', humidity: 80 },
    '深圳': { temp: 26, desc: '晴天', humidity: 55 },
    '杭州': { temp: 20, desc: '阴天', humidity: 70 }
  }
  
  const defaultWeather = { temp: 22, desc: '晴天', humidity: 50 }
  const weather = weatherData[city as keyof typeof weatherData] || defaultWeather
  
  const tempUnit = unit === 'fahrenheit' ? '°F' : '°C'
  const temp = unit === 'fahrenheit' ? Math.round(weather.temp * 9/5 + 32) : weather.temp
  
  return JSON.stringify({
    city,
    temperature: `${temp}${tempUnit}`,
    description: weather.desc,
    humidity: `${weather.humidity}%`,
    timestamp: new Date().toISOString()
  })
}

// 计算器工具执行
const executeCalculatorTool = async (args: { expression: string }): Promise<string> => {
  const { expression } = args
  
  try {
    // 安全的数学表达式计算 (仅支持基本运算)
    const sanitized = expression.replace(/[^0-9+\-*/().\s]/g, '')
    
    if (sanitized !== expression) {
      throw new Error('表达式包含不支持的字符')
    }
    
    // 使用 Function 构造器安全计算
    const result = new Function('return ' + sanitized)()
    
    if (typeof result !== 'number' || !isFinite(result)) {
      throw new Error('计算结果无效')
    }
    
    return JSON.stringify({
      expression,
      result,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    throw new Error(`计算失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

// 时间工具执行
const executeTimeTool = async (args: { timezone?: string }): Promise<string> => {
  const { timezone = 'Asia/Shanghai' } = args
  
  try {
    const now = new Date()
    const options: Intl.DateTimeFormatOptions = {
      timeZone: timezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      weekday: 'long'
    }
    
    const formatter = new Intl.DateTimeFormat('zh-CN', options)
    const timeString = formatter.format(now)
    
    return JSON.stringify({
      timezone,
      current_time: timeString,
      iso_time: now.toISOString(),
      timestamp: Date.now()
    })
  } catch (error) {
    throw new Error(`时间获取失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

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

  try {
    // 构建工具列表
    const tools = buildTools()
    
    // 构建完整的对话历史 (包括工具调用)
    const conversationHistory: any[] = []
    
    for (const msg of messages.value) {
      if (msg.type === 'user') {
        conversationHistory.push({
          role: 'user',
          content: msg.content
        })
      } else if (msg.type === 'ai') {
        const aiMsg: any = {
          role: 'assistant',
          content: msg.content
        }
        
        // 如果有工具调用，添加到消息中
        if (msg.toolCalls && msg.toolCalls.length > 0) {
          aiMsg.tool_calls = msg.toolCalls
        }
        
        conversationHistory.push(aiMsg)
        
        // 如果有工具调用，添加工具结果
        if (msg.toolResults) {
          for (const result of msg.toolResults) {
            conversationHistory.push({
              role: 'tool',
              tool_call_id: result.tool_call_id,
              content: result.content
            })
          }
        }
      }
    }

    // 发送请求
    const result = await sendMessageWithTools(message, tools, conversationHistory.slice(0, -1))
    
    // 处理响应
    const choice = result.choices[0]
    const responseMessage = choice.message
    
    // 如果有工具调用，执行工具并继续对话
    if (responseMessage.tool_calls && responseMessage.tool_calls.length > 0) {
      // 创建带工具调用的AI消息
      const aiMessageWithTools: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: responseMessage.content || '',
        toolCalls: responseMessage.tool_calls,
        timestamp: new Date()
      }
      
      messages.value.push(aiMessageWithTools)
      scrollToBottom()
      
      // 执行所有工具调用
      const toolResults = []
      for (const toolCall of responseMessage.tool_calls) {
        const toolResult = await executeToolCall(toolCall)
        toolResults.push({
          tool_call_id: toolCall.id,
          content: toolResult
        })
      }
      
      // 保存工具结果到消息中
      aiMessageWithTools.toolResults = toolResults
      
      // 构建包含工具结果的新对话历史
      const newConversationHistory = [...conversationHistory]
      newConversationHistory.push({
        role: 'assistant',
        content: responseMessage.content,
        tool_calls: responseMessage.tool_calls
      })
      
      for (const result of toolResults) {
        newConversationHistory.push({
          role: 'tool',
          tool_call_id: result.tool_call_id,
          content: result.content
        })
      }
      
      // 发送第二次请求获取最终回复
      const finalResult = await sendMessageWithTools('', tools, newConversationHistory)
      const finalChoice = finalResult.choices[0]
      
      // 创建最终AI回复
      const finalAiMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: 'ai',
        content: finalChoice.message.content || '处理完成',
        timestamp: new Date()
      }
      
      messages.value.push(finalAiMessage)
      scrollToBottom()
      
    } else {
      // 没有工具调用，直接显示回复
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: responseMessage.content || '收到回复',
        timestamp: new Date()
      }
      
      messages.value.push(aiMessage)
      scrollToBottom()
    }
    
  } catch (error) {
    console.error('发送消息失败:', error)
    
    // 添加错误消息
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: `错误: ${error instanceof Error ? error.message : '未知错误'}`,
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    scrollToBottom()
  }
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
/* 继承markdown样式 */
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
</style> 