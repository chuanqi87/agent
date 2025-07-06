import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 剪贴板工具 - 符合OpenAI标准
export const clipboardTool: ToolExecutor = {
  definition: {
    name: 'clipboard',
    description: '操作系统剪贴板，支持读取和写入文本内容',
    parameters: createParameterSchema({
      action: {
        type: 'string',
        enum: ['read', 'write'],
        description: '操作类型：read（读取剪贴板内容）、write（写入内容到剪贴板）'
      },
      text: {
        type: 'string',
        description: '要写入剪贴板的文本内容（仅write操作需要）'
      }
    }, ['action'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { action, text } = parameters
    
    try {
      // 检查剪贴板API是否可用
      if (!navigator.clipboard) {
        return '❌ 错误：浏览器不支持剪贴板API，请使用HTTPS协议访问'
      }
      
      switch (action) {
        case 'read':
          try {
            const clipboardText = await navigator.clipboard.readText()
            if (!clipboardText) {
              return '📋 剪贴板为空'
            }
            return `📋 剪贴板内容：${clipboardText}`
          } catch (error) {
            return '❌ 读取剪贴板失败：可能需要用户权限授权'
          }
          
        case 'write':
          if (text === undefined || text === '') {
            return '❌ 错误：write操作需要text参数'
          }
          try {
            await navigator.clipboard.writeText(text)
            return `✅ 已复制到剪贴板：${text}`
          } catch (error) {
            return '❌ 写入剪贴板失败：可能需要用户权限授权'
          }
          
        default:
          return '❌ 错误：无效的操作类型'
      }
    } catch (error) {
      return `❌ 剪贴板操作失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => {
    return typeof navigator !== 'undefined' && 
           'clipboard' in navigator && 
           typeof navigator.clipboard.readText === 'function' &&
           typeof navigator.clipboard.writeText === 'function'
  }
} 