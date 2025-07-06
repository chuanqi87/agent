import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import OpenAI from 'openai'
import type { ChatCompletionCreateParams } from 'openai/resources/chat/completions'
import { toolManager } from '../tools'

// 使用工具系统的Tool接口
import type { Tool } from '../utils/tools'

export const useApiStore = defineStore('api', () => {
  const isConnected = ref(false)
  const isThinking = ref(false)
  
  // 可配置的API设置
  const apiConfig = ref({
    baseURL: 'http://localhost:8000/v1',
    apiKey: 'dummy-key', // 本地部署通常不需要真实的API key
    model: 'deepseek-chat'
  })

  // 创建OpenAI客户端实例
  const createOpenAIClient = () => {
    return new OpenAI({
      baseURL: apiConfig.value.baseURL,
      apiKey: apiConfig.value.apiKey,
      dangerouslyAllowBrowser: true // 允许在浏览器中使用
    })
  }

  // 计算属性
  const canSendMessage = computed(() => isConnected.value && !isThinking.value)

  // 检查连接状态（使用OpenAI SDK）
  const checkConnection = async () => {
    try {
      console.log('正在检查连接状态...')
      const client = createOpenAIClient()
      
      // 发送一个简单的测试请求
      await client.chat.completions.create({
        model: apiConfig.value.model,
        messages: [{ role: 'user', content: 'test' }],
        max_tokens: 1,
        temperature: 0
      })
      
      isConnected.value = true
      console.log('✅ API连接正常')
      return true
    } catch (error) {
      console.error('❌ API连接检查失败:', error)
      isConnected.value = false
      return false
    }
  }

  // 初始化连接
  const connect = async () => {
    console.log('🔗 开始初始化API连接...')
    // 初始化工具系统
    toolManager.init()
    const result = await checkConnection()
    console.log('🔗 API连接结果:', result ? '成功' : '失败')
    return result
  }

  // 获取所有可用的工具
  const getAvailableTools = (): Tool[] => {
    return toolManager.getEnabledTools()
  }

  // 执行工具调用
  const executeToolCall = async (toolCall: any): Promise<string> => {
    return await toolManager.executeToolCall(toolCall)
  }

  // 统一的流式聊天方法，支持工具调用
  const streamChat = async (
    config: ChatCompletionCreateParams,
    onChunk: (chunk: any) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ) => {
    if (isThinking.value) return

    isThinking.value = true
    
    try {
      const client = createOpenAIClient()

      console.log('🌊 开始流式聊天:', {
        model: config.model,
        messages: config.messages.length,
        hasTools: Boolean(config.tools),
        toolsCount: config.tools?.length || 0
      })

      // 使用OpenAI SDK的流式API
      const stream = await client.chat.completions.create({
        ...config,
        stream: true
      })
      
      for await (const chunk of stream) {
        // 调用onChunk处理每个数据块
        onChunk(chunk)
        
        // 检查是否完成
        const finishReason = chunk.choices[0]?.finish_reason
        if (finishReason === 'stop' || finishReason === 'tool_calls') {
          console.log(`✅ 流式处理完成 (${finishReason})`)
          isThinking.value = false
          onComplete()
          break
        }
      }
      
    } catch (error) {
      console.error('❌ 流式聊天失败:', error)
      isThinking.value = false
      onError(error instanceof Error ? error.message : '流式聊天失败')
    }
  }

  const disconnect = () => {
    isConnected.value = false
    isThinking.value = false
  }

  // 更新API配置
  const updateApiConfig = (config: Partial<typeof apiConfig.value>) => {
    apiConfig.value = { ...apiConfig.value, ...config }
    console.log('📝 API配置已更新:', apiConfig.value)
  }

  // 获取当前API配置
  const getApiConfig = () => {
    return { ...apiConfig.value }
  }

  return {
    isConnected,
    isThinking,
    canSendMessage,
    apiConfig: computed(() => apiConfig.value),
    connect,
    disconnect,
    checkConnection,
    getAvailableTools,
    executeToolCall,
    updateApiConfig,
    getApiConfig,
    streamChat
  }
}) 