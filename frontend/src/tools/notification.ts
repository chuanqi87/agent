import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 通知工具 - 符合OpenAI标准
export const notificationTool: ToolExecutor = {
  definition: {
    name: 'notification',
    description: '显示浏览器通知，支持基本通知和富文本通知',
    parameters: createParameterSchema({
      action: {
        type: 'string',
        enum: ['show', 'permission'],
        description: '操作类型：show（显示通知）、permission（检查权限状态）'
      },
      title: {
        type: 'string',
        description: '通知标题（show操作必需）'
      },
      body: {
        type: 'string',
        description: '通知内容'
      },
      icon: {
        type: 'string',
        description: '通知图标URL（可选）'
      },
      tag: {
        type: 'string',
        description: '通知标签，用于分组和替换（可选）'
      }
    }, ['action'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { action, title, body, icon, tag } = parameters
    
    try {
      // 检查浏览器是否支持通知
      if (!('Notification' in window)) {
        return '❌ 错误：浏览器不支持通知功能'
      }
      
      switch (action) {
        case 'permission':
          const permission = Notification.permission
          let permissionText = ''
          
          switch (permission) {
            case 'granted':
              permissionText = '✅ 已授权：可以显示通知'
              break
            case 'denied':
              permissionText = '❌ 已拒绝：无法显示通知'
              break
            case 'default':
              permissionText = '⚠️ 未设置：需要请求权限'
              break
          }
          
          return `🔔 通知权限状态：${permissionText}`
          
        case 'show':
          if (!title) {
            return '❌ 错误：show操作需要title参数'
          }
          
          // 检查权限
          if (Notification.permission === 'denied') {
            return '❌ 错误：通知权限已被拒绝，请在浏览器设置中允许通知'
          }
          
          if (Notification.permission === 'default') {
            // 请求权限
            const permission = await Notification.requestPermission()
            if (permission !== 'granted') {
              return '❌ 用户拒绝了通知权限'
            }
          }
          
          // 创建通知选项
          const options: NotificationOptions = {}
          if (body) options.body = body
          if (icon) options.icon = icon
          if (tag) options.tag = tag
          
          // 显示通知
          const notification = new Notification(title, options)
          
          // 设置通知事件
          notification.onclick = () => {
            window.focus()
            notification.close()
          }
          
          // 3秒后自动关闭
          setTimeout(() => {
            notification.close()
          }, 3000)
          
          return `✅ 通知已显示：${title}${body ? `\n内容：${body}` : ''}`
          
        default:
          return '❌ 错误：无效的操作类型'
      }
    } catch (error) {
      return `❌ 通知操作失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => {
    return typeof window !== 'undefined' && 'Notification' in window
  }
} 