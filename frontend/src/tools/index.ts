// 工具注册器 - 统一管理所有工具
import { toolRegistry } from '../utils/tools'

// 导入所有工具
import { weatherTool } from './weather'
import { calculatorTool } from './calculator'
import { datetimeTool, timeCalculatorTool } from './datetime'
import { randomTool, uuidTool } from './random'

// 注册所有工具
export function registerAllTools() {
  // 基础工具
  toolRegistry.register(weatherTool)
  toolRegistry.register(calculatorTool)
  toolRegistry.register(datetimeTool)
  toolRegistry.register(timeCalculatorTool)
  
  // 实用工具
  toolRegistry.register(randomTool)
  toolRegistry.register(uuidTool)
  
  console.log(`🚀 工具注册完成，共注册 ${toolRegistry.getToolCount()} 个工具`)
  console.log(`📝 已注册的工具：${toolRegistry.getAllToolNames().join(', ')}`)
}

// 工具管理器
export class ToolManager {
  private static instance: ToolManager
  private initialized = false
  
  private constructor() {}
  
  static getInstance(): ToolManager {
    if (!ToolManager.instance) {
      ToolManager.instance = new ToolManager()
    }
    return ToolManager.instance
  }
  
  // 初始化工具系统
  init() {
    if (this.initialized) {
      console.log('⚠️ 工具系统已初始化')
      return
    }
    
    registerAllTools()
    this.initialized = true
    console.log('✅ 工具系统初始化完成')
  }
  
  // 获取所有启用的工具
  getEnabledTools() {
    return toolRegistry.getEnabledTools()
  }
  
  // 执行工具调用
  async executeToolCall(toolCall: any) {
    const { name, arguments: args } = toolCall.function
    
    try {
      const parsedArgs = JSON.parse(args)
      return await toolRegistry.execute(name, parsedArgs)
    } catch (error) {
      return `工具执行错误: ${error instanceof Error ? error.message : '未知错误'}`
    }
  }
  
  // 检查工具是否存在
  hasToolEnabled(name: string): boolean {
    const tool = toolRegistry.get(name)
    return tool ? (!tool.isEnabled || tool.isEnabled()) : false
  }
  
  // 获取工具信息
  getToolInfo(name: string) {
    const tool = toolRegistry.get(name)
    if (!tool) {
      return null
    }
    
    return {
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters,
      enabled: !tool.isEnabled || tool.isEnabled()
    }
  }
  
  // 获取所有工具信息
  getAllToolsInfo() {
    return toolRegistry.getAllToolNames().map(name => this.getToolInfo(name))
  }
}

// 导出工具管理器实例
export const toolManager = ToolManager.getInstance()

// 导出工具注册表（用于高级用法）
export { toolRegistry } from '../utils/tools' 