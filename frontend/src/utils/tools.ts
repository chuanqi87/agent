// 工具参数类型定义
export interface ToolParameter {
  type: string
  description?: string
  enum?: string[]
}

// 工具参数schema定义
export interface ToolParametersSchema {
  type: string
  properties: Record<string, ToolParameter>
  required?: string[]
}

// 工具函数定义
export interface ToolFunction {
  name: string
  description: string
  parameters?: ToolParametersSchema
}

// 完整的工具定义
export interface Tool {
  type: string
  function: ToolFunction
}

// 工具执行器接口
export interface ToolExecutor {
  name: string
  description: string
  parameters?: ToolParametersSchema
  execute: (args: any) => Promise<string>
  isEnabled?: () => boolean
}

// 工具注册表
class ToolRegistry {
  private tools: Map<string, ToolExecutor> = new Map()

  // 注册工具
  register(tool: ToolExecutor) {
    this.tools.set(tool.name, tool)
    console.log(`✅ 工具已注册: ${tool.name}`)
  }

  // 注销工具
  unregister(name: string) {
    this.tools.delete(name)
    console.log(`❌ 工具已注销: ${name}`)
  }

  // 获取工具
  get(name: string): ToolExecutor | undefined {
    return this.tools.get(name)
  }

  // 获取所有已启用的工具
  getEnabledTools(): Tool[] {
    const enabledTools: Tool[] = []
    
    for (const [name, executor] of this.tools) {
      // 检查工具是否启用
      if (!executor.isEnabled || executor.isEnabled()) {
        enabledTools.push({
          type: 'function',
          function: {
            name: executor.name,
            description: executor.description,
            parameters: executor.parameters
          }
        })
      }
    }
    
    return enabledTools
  }

  // 执行工具
  async execute(name: string, args: any): Promise<string> {
    const tool = this.tools.get(name)
    if (!tool) {
      throw new Error(`未找到工具: ${name}`)
    }

    try {
      console.log(`🔧 执行工具: ${name}`, args)
      const result = await tool.execute(args)
      console.log(`✅ 工具执行成功: ${name}`)
      return result
    } catch (error) {
      console.error(`❌ 工具执行失败: ${name}`, error)
      throw error
    }
  }

  // 获取所有工具名称
  getAllToolNames(): string[] {
    return Array.from(this.tools.keys())
  }

  // 获取工具数量
  getToolCount(): number {
    return this.tools.size
  }
}

// 全局工具注册表实例
export const toolRegistry = new ToolRegistry()

// 工具执行辅助函数
export async function executeToolCall(toolCall: any): Promise<string> {
  const { name, arguments: args } = toolCall.function
  
  try {
    const parsedArgs = JSON.parse(args)
    return await toolRegistry.execute(name, parsedArgs)
  } catch (error) {
    return `工具执行错误: ${error instanceof Error ? error.message : '未知错误'}`
  }
} 