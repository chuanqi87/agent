import type { ToolExecutor } from '../utils/tools'

// 天气查询工具
export const weatherTool: ToolExecutor = {
  name: 'get_weather',
  description: '获取指定城市的天气信息',
  parameters: {
    type: 'object',
    properties: {
      city: {
        type: 'string',
        description: '城市名称，例如：北京、上海、广州'
      }
    },
    required: ['city']
  },
  
  async execute(args: { city: string }): Promise<string> {
    const { city } = args
    
    // 模拟天气查询API调用
    // 在实际应用中，这里应该调用真实的天气API
    const weatherData = {
      '北京': { temperature: '15°C', condition: '晴', humidity: '45%' },
      '上海': { temperature: '18°C', condition: '多云', humidity: '60%' },
      '广州': { temperature: '25°C', condition: '小雨', humidity: '80%' },
      '深圳': { temperature: '24°C', condition: '晴', humidity: '70%' },
      '杭州': { temperature: '16°C', condition: '阴', humidity: '55%' }
    }
    
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const weather = weatherData[city as keyof typeof weatherData]
    
    if (weather) {
      return `${city}的天气情况：
温度: ${weather.temperature}
天气: ${weather.condition}
湿度: ${weather.humidity}`
    } else {
      return `抱歉，暂时无法获取${city}的天气信息。支持的城市包括：北京、上海、广州、深圳、杭州。`
    }
  },
  
  // 工具是否启用的检查函数
  isEnabled: () => true
} 