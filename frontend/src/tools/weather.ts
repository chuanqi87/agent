import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 天气查询工具 - 符合OpenAI标准
export const weatherTool: ToolExecutor = {
  definition: {
    name: 'get_weather',
    description: '获取指定城市的天气信息，包括温度、天气状况和湿度',
    parameters: createParameterSchema({
      city: {
        type: 'string',
        description: '城市名称，例如：北京、上海、广州、深圳、杭州等中国主要城市'
      }
    }, ['city'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { city } = parameters
    
    // 模拟天气查询API调用
    // 在实际应用中，这里应该调用真实的天气API
    const weatherData = {
      '北京': { temperature: '15°C', condition: '晴', humidity: '45%', windSpeed: '3级' },
      '上海': { temperature: '18°C', condition: '多云', humidity: '60%', windSpeed: '2级' },
      '广州': { temperature: '25°C', condition: '小雨', humidity: '80%', windSpeed: '1级' },
      '深圳': { temperature: '24°C', condition: '晴', humidity: '70%', windSpeed: '2级' },
      '杭州': { temperature: '16°C', condition: '阴', humidity: '55%', windSpeed: '3级' },
      '成都': { temperature: '20°C', condition: '多云', humidity: '65%', windSpeed: '1级' },
      '重庆': { temperature: '22°C', condition: '雾', humidity: '75%', windSpeed: '1级' },
      '南京': { temperature: '17°C', condition: '晴', humidity: '50%', windSpeed: '2级' },
      '武汉': { temperature: '19°C', condition: '小雨', humidity: '70%', windSpeed: '2级' },
      '西安': { temperature: '14°C', condition: '晴', humidity: '40%', windSpeed: '3级' }
    }
    
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const weather = weatherData[city as keyof typeof weatherData]
    
    if (weather) {
      return `${city}的天气情况：
🌡️ 温度: ${weather.temperature}
🌤️ 天气: ${weather.condition}
💧 湿度: ${weather.humidity}
💨 风力: ${weather.windSpeed}

数据更新时间: ${new Date().toLocaleString('zh-CN')}`
    } else {
      const supportedCities = Object.keys(weatherData).join('、')
      return `抱歉，暂时无法获取${city}的天气信息。

支持的城市包括：${supportedCities}

请提供准确的城市名称，或者选择上述支持的城市之一。`
    }
  },
  
  // 工具是否启用的检查函数
  isEnabled: () => true
} 