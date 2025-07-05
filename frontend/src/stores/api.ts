import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { toolManager } from '../tools'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system' | 'tool'
  content?: string
  name?: string
  tool_call_id?: string
  tool_calls?: any[]
}

interface ChatResponse {
  id: string
  object: string
  created: number
  model: string
  choices: {
    index: number
    message: {
      role: string
      content: string
    }
    finish_reason: string
  }[]
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

// 使用工具系统的Tool接口
import type { Tool } from '../utils/tools'

export const useApiStore = defineStore('api', () => {
  const isConnected = ref(false)
  const isThinking = ref(false)
  const baseUrl = 'http://localhost:8000'

  // 计算属性
  const canSendMessage = computed(() => isConnected.value && !isThinking.value)

  // 检查连接状态
  const checkConnection = async () => {
    try {
      console.log('正在检查连接状态...')
      const response = await fetch(`${baseUrl}/health`)
      console.log('连接检查响应:', response.status, response.ok)
      isConnected.value = response.ok
      if (response.ok) {
        console.log('✅ 后端连接正常')
      } else {
        console.warn('❌ 后端连接失败，状态码:', response.status)
      }
      return response.ok
    } catch (error) {
      console.error('❌ 连接检查失败:', error)
      isConnected.value = false
      return false
    }
  }

  // 使用SSE流式发送消息
  const sendMessageStream = (
    message: string, 
    conversationHistory: ChatMessage[] = [],
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ) => {
    if (isThinking.value) return

    isThinking.value = true
    
    // 构建消息历史
    const messages: ChatMessage[] = [
      ...conversationHistory,
      { role: 'user', content: message }
    ]

    // 创建POST请求的参数
    const requestBody = JSON.stringify({
      model: 'deepseek-chat',
      messages: messages,
      temperature: 0.7,
      max_tokens: 2000,
      stream: true
    })

    // 使用fetch实现SSE（因为EventSource不支持POST）
    fetch(`${baseUrl}/v1/chat/completions/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: requestBody
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法获取响应流')
      }

      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      const readStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read()
            
            if (done) {
              console.log('✅ SSE流结束')
              isThinking.value = false
              onComplete()
              break
            }

            // 解码新数据并添加到缓冲区
            const chunk = decoder.decode(value, { stream: true })
            // console.log('📥 收到原始数据块:', chunk)  // 注释掉减少日志
            buffer += chunk
            
            // 处理完整的行
            const lines = buffer.split('\n')
            buffer = lines.pop() || '' // 保留可能不完整的最后一行

            for (const line of lines) {
              const trimmedLine = line.trim()
              // console.log('🔍 处理行:', trimmedLine)  // 注释掉减少日志
              
              if (trimmedLine.startsWith('data: ')) {
                const data = trimmedLine.slice(6).trim()
                // console.log('📝 SSE数据:', data)  // 注释掉减少日志
                
                if (data === '[DONE]') {
                  console.log('✅ SSE消息完成')
                  isThinking.value = false
                  onComplete()
                  return
                }

                if (data === '') {
                  // 空的data行，跳过
                  continue
                }

                try {
                  const parsed = JSON.parse(data)
                  // console.log('📋 解析后的数据:', parsed)  // 注释掉减少日志
                  
                  const choice = parsed.choices?.[0]
                  const delta = choice?.delta
                  const content = delta?.content
                  const finishReason = choice?.finish_reason
                  
                  if (content) {
                    console.log('✏️ 内容片段:', content)
                    onChunk(content)
                  } else if (delta?.role) {
                    console.log('👤 角色信息:', delta.role)
                    // 开始消息，不需要显示
                  }
                  
                  // 检查是否完成
                  if (finishReason === 'stop') {
                    console.log('✅ SSE消息通过finish_reason完成')
                    isThinking.value = false
                    onComplete()
                    return
                  }
                } catch (e) {
                  console.warn('❌ 解析SSE数据失败:', data, e)
                }
              }
            }
          }
        } catch (error) {
          console.error('❌ 读取SSE流失败:', error)
          isThinking.value = false
          onError(error instanceof Error ? error.message : '读取流失败')
        }
      }

      readStream()
    })
    .catch(error => {
      console.error('SSE请求失败:', error)
      isThinking.value = false
      onError(error instanceof Error ? error.message : 'SSE请求失败')
    })
  }

  // 发送消息到AI (非流式，保持兼容性)
  const sendMessage = async (message: string, conversationHistory: ChatMessage[] = []) => {
    if (isThinking.value) return null

    try {
      isThinking.value = true

      // 构建消息历史
      const messages: ChatMessage[] = [
        ...conversationHistory,
        { role: 'user', content: message }
      ]

      const response = await fetch(`${baseUrl}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: messages,
          temperature: 0.7,
          max_tokens: 2000,
          stream: false
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`)
      }

      const data: ChatResponse = await response.json()
      return data.choices[0]?.message?.content || '抱歉，我没有收到有效的回复。'

    } catch (error) {
      console.error('发送消息失败:', error)
      throw new Error(error instanceof Error ? error.message : '发送消息失败')
    } finally {
      isThinking.value = false
    }
  }

  // 获取可用模型
  const getModels = async () => {
    try {
      const response = await fetch(`${baseUrl}/v1/models`)
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('获取模型列表失败:', error)
      throw error
    }
  }

  // 初始化连接检查
  const connect = async () => {
    console.log('🔗 开始初始化连接...')
    // 初始化工具系统
    toolManager.init()
    const result = await checkConnection()
    console.log('🔗 初始连接结果:', result, 'isConnected:', isConnected.value)
    // 定期检查连接状态
    setInterval(checkConnection, 30000) // 每30秒检查一次
  }

  // 获取所有可用的工具
  const getAvailableTools = (): Tool[] => {
    return toolManager.getEnabledTools()
  }

  // 执行工具调用
  const executeToolCall = async (toolCall: any): Promise<string> => {
    return await toolManager.executeToolCall(toolCall)
  }

  const disconnect = () => {
    isConnected.value = false
    isThinking.value = false
  }

  // 发送带有工具的消息（非流式）
  const sendMessageWithTools = async (
    message: string,
    tools: Tool[],
    conversationHistory: ChatMessage[] = []
  ): Promise<any> => {
    if (!isConnected.value || isThinking.value) {
      throw new Error('连接不可用或正在处理中')
    }

    isThinking.value = true

    try {
      // 构建消息列表，只有在message不为空时才添加用户消息
      const messages = [...conversationHistory]
      if (message.trim()) {
        messages.push({ role: 'user', content: message })
      }

      const requestBody = {
        model: 'deepseek-chat',
        messages: messages,
        tools: tools,
        tool_choice: 'auto',
        temperature: 0.7,
        max_tokens: 2000
      }

      console.log('🔍 发送Function Calling请求:', JSON.stringify(requestBody, null, 2))

      const response = await fetch(`${baseUrl}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('API错误响应:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
      }

      const result = await response.json()
      return result

    } catch (error) {
      console.error('工具调用请求失败:', error)
      throw error
    } finally {
      isThinking.value = false
    }
  }

  return {
    isConnected,
    isThinking,
    canSendMessage,
    connect,
    disconnect,
    sendMessage,
    sendMessageStream,
    getModels,
    checkConnection,
    sendMessageWithTools,
    getAvailableTools,
    executeToolCall
  }
}) 