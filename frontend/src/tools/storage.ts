import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 本地存储工具 - 符合OpenAI标准
export const localStorageTool: ToolExecutor = {
  definition: {
    name: 'local_storage',
    description: '操作浏览器本地存储（localStorage），支持存储、读取、删除数据，数据持久保存',
    parameters: createParameterSchema({
      action: {
        type: 'string',
        enum: ['set', 'get', 'remove', 'clear', 'list'],
        description: '操作类型：set（存储）、get（读取）、remove（删除）、clear（清空）、list（列出所有键）'
      },
      key: {
        type: 'string',
        description: '存储键名（set、get、remove操作必需）'
      },
      value: {
        type: 'string',
        description: '存储值（仅set操作需要）'
      }
    }, ['action'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { action, key, value } = parameters
    
    try {
      switch (action) {
        case 'set':
          if (!key || value === undefined) {
            return '❌ 错误：set操作需要key和value参数'
          }
          localStorage.setItem(key, value)
          return `✅ 已存储数据：${key} = ${value}`
          
        case 'get':
          if (!key) {
            return '❌ 错误：get操作需要key参数'
          }
          const storedValue = localStorage.getItem(key)
          if (storedValue === null) {
            return `⚠️ 未找到键：${key}`
          }
          return `📄 读取数据：${key} = ${storedValue}`
          
        case 'remove':
          if (!key) {
            return '❌ 错误：remove操作需要key参数'
          }
          localStorage.removeItem(key)
          return `🗑️ 已删除键：${key}`
          
        case 'clear':
          localStorage.clear()
          return '🧹 已清空所有本地存储数据'
          
        case 'list':
          const keys = Object.keys(localStorage)
          if (keys.length === 0) {
            return '📭 本地存储为空'
          }
          return `📋 本地存储键列表（共${keys.length}个）：\n${keys.join(', ')}`
          
        default:
          return '❌ 错误：无效的操作类型'
      }
    } catch (error) {
      return `❌ 本地存储操作失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => typeof localStorage !== 'undefined'
}

// 会话存储工具 - 符合OpenAI标准
export const sessionStorageTool: ToolExecutor = {
  definition: {
    name: 'session_storage',
    description: '操作浏览器会话存储（sessionStorage），数据仅在当前标签页会话期间保存',
    parameters: createParameterSchema({
      action: {
        type: 'string',
        enum: ['set', 'get', 'remove', 'clear', 'list'],
        description: '操作类型：set（存储）、get（读取）、remove（删除）、clear（清空）、list（列出所有键）'
      },
      key: {
        type: 'string',
        description: '存储键名（set、get、remove操作必需）'
      },
      value: {
        type: 'string',
        description: '存储值（仅set操作需要）'
      }
    }, ['action'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { action, key, value } = parameters
    
    try {
      switch (action) {
        case 'set':
          if (!key || value === undefined) {
            return '❌ 错误：set操作需要key和value参数'
          }
          sessionStorage.setItem(key, value)
          return `✅ 已存储会话数据：${key} = ${value}`
          
        case 'get':
          if (!key) {
            return '❌ 错误：get操作需要key参数'
          }
          const storedValue = sessionStorage.getItem(key)
          if (storedValue === null) {
            return `⚠️ 未找到键：${key}`
          }
          return `📄 读取会话数据：${key} = ${storedValue}`
          
        case 'remove':
          if (!key) {
            return '❌ 错误：remove操作需要key参数'
          }
          sessionStorage.removeItem(key)
          return `🗑️ 已删除会话键：${key}`
          
        case 'clear':
          sessionStorage.clear()
          return '🧹 已清空所有会话存储数据'
          
        case 'list':
          const keys = Object.keys(sessionStorage)
          if (keys.length === 0) {
            return '📭 会话存储为空'
          }
          return `📋 会话存储键列表（共${keys.length}个）：\n${keys.join(', ')}`
          
        default:
          return '❌ 错误：无效的操作类型'
      }
    } catch (error) {
      return `❌ 会话存储操作失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => typeof sessionStorage !== 'undefined'
} 