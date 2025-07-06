import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 随机数生成工具 - 符合OpenAI标准
export const randomTool: ToolExecutor = {
  definition: {
    name: 'generate_random',
    description: '生成指定范围内的随机数，支持整数和浮点数',
    parameters: createParameterSchema({
      min: {
        type: 'number',
        description: '最小值（包含）'
      },
      max: {
        type: 'number',
        description: '最大值（不包含）'
      },
      count: {
        type: 'number',
        description: '生成的随机数数量，默认为1，最大100'
      },
      type: {
        type: 'string',
        enum: ['integer', 'float'],
        description: '随机数类型：integer（整数）或float（浮点数），默认为integer'
      }
    }, ['min', 'max'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { min, max, count = 1, type = 'integer' } = parameters
    
    // 验证参数
    if (min >= max) {
      return '❌ 错误：最小值必须小于最大值'
    }
    
    if (count < 1 || count > 100) {
      return '❌ 错误：生成数量必须在1到100之间'
    }
    
    const results: number[] = []
    
    for (let i = 0; i < count; i++) {
      const random = Math.random() * (max - min) + min
      
      if (type === 'integer') {
        results.push(Math.floor(random))
      } else {
        results.push(Math.round(random * 100) / 100) // 保留2位小数
      }
    }
    
    if (count === 1) {
      return `🎲 生成的随机${type === 'integer' ? '整数' : '浮点数'}：${results[0]}`
    } else {
      return `🎲 生成的${count}个随机${type === 'integer' ? '整数' : '浮点数'}：
${results.join(', ')}`
    }
  },
  
  isEnabled: () => true
}

// UUID生成工具 - 符合OpenAI标准
export const uuidTool: ToolExecutor = {
  definition: {
    name: 'generate_uuid',
    description: '生成UUID（通用唯一标识符），支持标准UUID v4和简化版本',
    parameters: createParameterSchema({
      version: {
        type: 'string',
        enum: ['v4', 'simple'],
        description: 'UUID版本：v4（标准UUID）或simple（简化版），默认为v4'
      },
      count: {
        type: 'number',
        description: '生成的UUID数量，默认为1，最大10'
      }
    })
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { version = 'v4', count = 1 } = parameters
    
    if (count < 1 || count > 10) {
      return '❌ 错误：生成数量必须在1到10之间'
    }
    
    const results: string[] = []
    
    for (let i = 0; i < count; i++) {
      if (version === 'v4') {
        // 生成标准UUID v4
        const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          const r = Math.random() * 16 | 0
          const v = c === 'x' ? r : (r & 0x3 | 0x8)
          return v.toString(16)
        })
        results.push(uuid)
      } else {
        // 生成简化版UUID
        const timestamp = Date.now().toString(36)
        const randomPart = Math.random().toString(36).substring(2, 8)
        results.push(`${timestamp}-${randomPart}`)
      }
    }
    
    if (count === 1) {
      return `🆔 生成的UUID（${version}）：
${results[0]}`
    } else {
      return `🆔 生成的${count}个UUID（${version}）：
${results.map((uuid, index) => `${index + 1}. ${uuid}`).join('\n')}`
    }
  },
  
  isEnabled: () => true
} 