import type { ToolExecutor } from '../utils/tools'

// 计算器工具
export const calculatorTool: ToolExecutor = {
  name: 'calculate',
  description: '执行数学计算，支持基本的算术运算',
  parameters: {
    type: 'object',
    properties: {
      expression: {
        type: 'string',
        description: '要计算的数学表达式，例如：2+3*4、10/2、sqrt(16)、sin(30)'
      }
    },
    required: ['expression']
  },
  
  async execute(args: { expression: string }): Promise<string> {
    const { expression } = args
    
    try {
      // 安全的数学表达式计算
      const result = evaluateExpression(expression)
      return `计算结果：${expression} = ${result}`
    } catch (error) {
      return `计算错误：${error instanceof Error ? error.message : '无效的数学表达式'}`
    }
  },
  
  isEnabled: () => true
}

// 安全的数学表达式计算函数
function evaluateExpression(expr: string): number {
  // 清理表达式，移除空格
  expr = expr.replace(/\s+/g, '')
  
  // 支持的数学函数
  const mathFunctions = {
    sin: Math.sin,
    cos: Math.cos,
    tan: Math.tan,
    sqrt: Math.sqrt,
    abs: Math.abs,
    floor: Math.floor,
    ceil: Math.ceil,
    round: Math.round,
    log: Math.log,
    ln: Math.log,
    log10: Math.log10,
    exp: Math.exp,
    pow: Math.pow,
    pi: Math.PI,
    e: Math.E
  }
  
  // 替换数学函数
  let processedExpr = expr
  for (const [name, func] of Object.entries(mathFunctions)) {
    if (typeof func === 'number') {
      processedExpr = processedExpr.replace(new RegExp(name, 'g'), func.toString())
    } else {
      processedExpr = processedExpr.replace(
        new RegExp(`${name}\\(([^)]+)\\)`, 'g'),
        (match, args) => {
          const argValue = evaluateExpression(args)
          return (func as Function)(argValue).toString()
        }
      )
    }
  }
  
  // 验证表达式只包含安全字符
  const safePattern = /^[0-9+\-*/.() ]+$/
  if (!safePattern.test(processedExpr)) {
    throw new Error('表达式包含不安全的字符')
  }
  
  // 使用Function构造函数安全计算
  try {
    const result = new Function('return ' + processedExpr)()
    
    if (typeof result !== 'number' || !isFinite(result)) {
      throw new Error('计算结果无效')
    }
    
    return result
  } catch (error) {
    throw new Error('无法计算表达式')
  }
} 