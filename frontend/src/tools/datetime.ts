import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 日期时间工具 - 符合OpenAI标准
export const datetimeTool: ToolExecutor = {
  definition: {
    name: 'get_current_time',
    description: '获取当前的日期和时间信息，支持多种格式和时区',
    parameters: createParameterSchema({
      format: {
        type: 'string',
        description: '时间格式，可选值：datetime（日期时间）、date（仅日期）、time（仅时间）、timestamp（时间戳）',
        enum: ['datetime', 'date', 'time', 'timestamp']
      },
      timezone: {
        type: 'string',
        description: '时区，例如：Asia/Shanghai、UTC、America/New_York，默认为Asia/Shanghai'
      }
    })
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { format = 'datetime', timezone = 'Asia/Shanghai' } = parameters
    
    try {
      const now = new Date()
      
      // 根据时区调整时间
      const options: Intl.DateTimeFormatOptions = {
        timeZone: timezone
      }
      
      switch (format) {
        case 'date':
          options.year = 'numeric'
          options.month = '2-digit'
          options.day = '2-digit'
          return `当前日期：${now.toLocaleDateString('zh-CN', options)}`
          
        case 'time':
          options.hour = '2-digit'
          options.minute = '2-digit'
          options.second = '2-digit'
          return `当前时间：${now.toLocaleTimeString('zh-CN', options)}`
          
        case 'timestamp':
          return `当前时间戳：${now.getTime()}`
          
        case 'datetime':
        default:
          options.year = 'numeric'
          options.month = '2-digit'
          options.day = '2-digit'
          options.hour = '2-digit'
          options.minute = '2-digit'
          options.second = '2-digit'
          options.weekday = 'long'
          
          const dateTimeStr = now.toLocaleString('zh-CN', options)
          return `当前时间：${dateTimeStr}（时区：${timezone}）`
      }
    } catch (error) {
      return `获取时间失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => true
}

// 时间计算工具 - 符合OpenAI标准
export const timeCalculatorTool: ToolExecutor = {
  definition: {
    name: 'calculate_time',
    description: '计算时间差或时间加减运算，支持多种时间单位和操作',
    parameters: createParameterSchema({
      operation: {
        type: 'string',
        description: '操作类型：add（加）、subtract（减）、diff（计算差值）',
        enum: ['add', 'subtract', 'diff']
      },
      base_time: {
        type: 'string',
        description: '基准时间，格式：YYYY-MM-DD HH:mm:ss 或 now（当前时间），默认为now'
      },
      amount: {
        type: 'number',
        description: '时间数量（仅用于add和subtract操作）'
      },
      unit: {
        type: 'string',
        description: '时间单位：years、months、days、hours、minutes、seconds',
        enum: ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
      },
      target_time: {
        type: 'string',
        description: '目标时间（仅用于diff操作），格式：YYYY-MM-DD HH:mm:ss'
      }
    }, ['operation'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { 
      operation, 
      base_time = 'now', 
      amount = 0, 
      unit = 'days', 
      target_time 
    } = parameters
    
    try {
      // 解析基准时间
      let baseDate: Date
      if (base_time === 'now') {
        baseDate = new Date()
      } else {
        baseDate = new Date(base_time)
        if (isNaN(baseDate.getTime())) {
          throw new Error('无效的基准时间格式')
        }
      }
      
      switch (operation) {
        case 'add':
          const addedDate = addTime(baseDate, amount, unit)
          return `时间计算结果：${baseDate.toLocaleString('zh-CN')} + ${amount} ${unit} = ${addedDate.toLocaleString('zh-CN')}`
          
        case 'subtract':
          const subtractedDate = addTime(baseDate, -amount, unit)
          return `时间计算结果：${baseDate.toLocaleString('zh-CN')} - ${amount} ${unit} = ${subtractedDate.toLocaleString('zh-CN')}`
          
        case 'diff':
          if (!target_time) {
            throw new Error('diff操作需要提供target_time参数')
          }
          const targetDate = new Date(target_time)
          if (isNaN(targetDate.getTime())) {
            throw new Error('无效的目标时间格式')
          }
          
          const diffMs = Math.abs(targetDate.getTime() - baseDate.getTime())
          const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
          const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
          const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
          
          return `时间差计算结果：${baseDate.toLocaleString('zh-CN')} 与 ${targetDate.toLocaleString('zh-CN')} 相差 ${diffDays}天 ${diffHours}小时 ${diffMinutes}分钟`
          
        default:
          throw new Error('不支持的操作类型')
      }
    } catch (error) {
      return `时间计算失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => true
}

// 时间加减辅助函数
function addTime(date: Date, amount: number, unit: string): Date {
  const result = new Date(date)
  
  switch (unit) {
    case 'years':
      result.setFullYear(result.getFullYear() + amount)
      break
    case 'months':
      result.setMonth(result.getMonth() + amount)
      break
    case 'days':
      result.setDate(result.getDate() + amount)
      break
    case 'hours':
      result.setHours(result.getHours() + amount)
      break
    case 'minutes':
      result.setMinutes(result.getMinutes() + amount)
      break
    case 'seconds':
      result.setSeconds(result.getSeconds() + amount)
      break
    default:
      throw new Error('不支持的时间单位')
  }
  
  return result
} 