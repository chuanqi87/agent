import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 浏览器信息工具 - 符合OpenAI标准
export const browserInfoTool: ToolExecutor = {
  definition: {
    name: 'browser_info',
    description: '获取浏览器、设备、屏幕等信息，包括用户代理、屏幕分辨率、时区、语言等。不指定type时默认返回所有信息',
    parameters: createParameterSchema({
      type: {
        type: 'string',
        enum: ['all', 'browser', 'screen', 'device', 'network', 'location'],
        description: '信息类型：all（全部，默认）、browser（浏览器）、screen（屏幕）、device（设备）、network（网络）、location（位置）'
      }
    }, [])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { type = 'all' } = parameters
    
    try {
      const getBrowserInfo = () => {
        const ua = navigator.userAgent
        const browser = {
          userAgent: ua,
          language: navigator.language,
          languages: navigator.languages?.join(', ') || 'N/A',
          platform: navigator.platform,
          cookieEnabled: navigator.cookieEnabled,
          onLine: navigator.onLine ? '在线' : '离线',
          vendor: navigator.vendor || 'N/A'
        }
        
        return `🌐 浏览器信息：
📱 用户代理：${browser.userAgent}
🗣️ 语言：${browser.language}
🌍 支持语言：${browser.languages}
💻 平台：${browser.platform}
🍪 Cookie启用：${browser.cookieEnabled ? '是' : '否'}
📡 网络状态：${browser.onLine}
🏢 浏览器厂商：${browser.vendor}`
      }
      
      const getScreenInfo = () => {
        const screen = window.screen
        const viewport = {
          width: window.innerWidth,
          height: window.innerHeight
        }
        
        return `🖥️ 屏幕信息：
📐 屏幕分辨率：${screen.width} × ${screen.height}
🎨 颜色深度：${screen.colorDepth} 位
📱 视窗大小：${viewport.width} × ${viewport.height}
🔆 可用屏幕：${screen.availWidth} × ${screen.availHeight}
📏 像素比：${window.devicePixelRatio || 1}`
      }
      
      const getDeviceInfo = () => {
        const memory = (navigator as any).deviceMemory || 'N/A'
        const cores = navigator.hardwareConcurrency || 'N/A'
        const connection = (navigator as any).connection
        
        let deviceInfo = `⚙️ 设备信息：
🧠 内存：${memory} GB
⚡ CPU核心：${cores}
⏰ 时区：${Intl.DateTimeFormat().resolvedOptions().timeZone}`
        
        if (connection) {
          deviceInfo += `
📶 网络类型：${connection.effectiveType || 'N/A'}
🚀 下行速度：${connection.downlink || 'N/A'} Mbps`
        }
        
        return deviceInfo
      }
      
      const getLocationInfo = () => {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
        const locale = Intl.DateTimeFormat().resolvedOptions().locale
        
        return `📍 位置信息：
⏰ 时区：${timezone}
🌍 地区：${locale}
⏱️ 当前时间：${new Date().toLocaleString()}`
      }
      
      const getNetworkInfo = () => {
        const connection = (navigator as any).connection
        if (!connection) {
          return '📡 网络信息：浏览器不支持Network Information API'
        }
        
        return `📡 网络信息：
🌐 连接类型：${connection.type || 'N/A'}
📶 有效类型：${connection.effectiveType || 'N/A'}
🚀 下行速度：${connection.downlink || 'N/A'} Mbps
📈 往返时间：${connection.rtt || 'N/A'} ms
💾 数据节省：${connection.saveData ? '启用' : '关闭'}`
      }
      
      switch (type) {
        case 'browser':
          return getBrowserInfo()
          
        case 'screen':
          return getScreenInfo()
          
        case 'device':
          return getDeviceInfo()
          
        case 'network':
          return getNetworkInfo()
          
        case 'location':
          return getLocationInfo()
          
        case 'all':
        default:
          return `${getBrowserInfo()}

${getScreenInfo()}

${getDeviceInfo()}

${getLocationInfo()}

${getNetworkInfo()}`
      }
    } catch (error) {
      return `❌ 获取浏览器信息失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => typeof navigator !== 'undefined' && typeof window !== 'undefined'
} 