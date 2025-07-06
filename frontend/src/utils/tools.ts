import type { ChatCompletionTool } from 'openai/resources/chat/completions'

// 使用OpenAI标准的工具定义类型
export type Tool = ChatCompletionTool

// 工具执行器接口，符合OpenAI标准
export interface ToolExecutor {
  // 工具的基本信息
  definition: ChatCompletionTool['function']
  // 执行函数，接收参数并返回结果
  execute: (parameters: Record<string, any>) => Promise<string>
  // 是否启用该工具
  isEnabled?: () => boolean
}

// 工具注册表，管理所有可用的工具
class ToolRegistry {
  private tools: Map<string, ToolExecutor> = new Map()

  // 注册工具
  register(tool: ToolExecutor) {
    this.tools.set(tool.definition.name, tool)
    console.log(`✅ 工具已注册: ${tool.definition.name}`)
  }

  // 注销工具
  unregister(name: string) {
    if (this.tools.delete(name)) {
      console.log(`❌ 工具已注销: ${name}`)
    }
  }

  // 获取工具执行器
  get(name: string): ToolExecutor | undefined {
    return this.tools.get(name)
  }

  // 获取所有已启用的工具（OpenAI格式）
  getEnabledTools(): Tool[] {
    const enabledTools: Tool[] = []
    
    for (const [name, executor] of this.tools) {
      // 检查工具是否启用
      if (!executor.isEnabled || executor.isEnabled()) {
        enabledTools.push({
          type: 'function',
          function: executor.definition
        })
      }
    }
    
    return enabledTools
  }

  // 执行工具调用
  async execute(name: string, parameters: Record<string, any>): Promise<string> {
    const tool = this.tools.get(name)
    if (!tool) {
      throw new Error(`工具不存在: ${name}`)
    }

    try {
      console.log(`🔧 执行工具: ${name}`, parameters)
      
      // 验证参数（基本验证，可以根据需要扩展）
      if (tool.definition.parameters?.required && Array.isArray(tool.definition.parameters.required)) {
        for (const requiredParam of tool.definition.parameters.required) {
          if (!(requiredParam in parameters)) {
            throw new Error(`缺少必需参数: ${requiredParam}`)
          }
        }
      }

      const result = await tool.execute(parameters)
      console.log(`✅ 工具执行成功: ${name}`)
      return result
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知错误'
      console.error(`❌ 工具执行失败: ${name}`, errorMessage)
      return `工具执行失败: ${errorMessage}`
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

  // 清空所有工具
  clear() {
    this.tools.clear()
    console.log('🧹 已清空所有工具')
  }
}

// 全局工具注册表实例
export const toolRegistry = new ToolRegistry()

// OpenAI标准的工具调用执行函数
export async function executeToolCall(toolCall: {
  id: string
  type: 'function'
  function: {
    name: string
    arguments: string
  }
}): Promise<string> {
  try {
    // 解析参数
    const parameters = JSON.parse(toolCall.function.arguments)
    
    // 执行工具
    return await toolRegistry.execute(toolCall.function.name, parameters)
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    console.error('工具调用失败:', errorMessage)
    return `工具调用失败: ${errorMessage}`
  }
}

// 辅助函数：创建JSONSchema格式的参数定义
export function createParameterSchema(properties: Record<string, {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  description?: string
  enum?: any[]
  items?: any
  properties?: any
}>, required?: string[]) {
  return {
    type: 'object' as const,
    properties,
    required: required || [],
    additionalProperties: false
  }
} 