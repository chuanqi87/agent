import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 计算器工具 - 符合OpenAI标准
export const calculatorTool: ToolExecutor = {
  definition: {
    name: 'calculate',
    description: '执行数学计算，支持基本的算术运算、三角函数、对数函数等',
    parameters: createParameterSchema({
      expression: {
        type: 'string',
        description: '要计算的数学表达式。支持：+、-、*、/、^、()、sin、cos、tan、sqrt、abs、log、ln、exp、pi、e等。例如：2+3*4、sqrt(16)、sin(30*pi/180)'
      }
    }, ['expression'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { expression } = parameters as { expression: string }
    
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
  
  // 支持的数学函数和常量
  const mathFunctions = {
    // 三角函数
    sin: Math.sin,
    cos: Math.cos,
    tan: Math.tan,
    asin: Math.asin,
    acos: Math.acos,
    atan: Math.atan,
    // 基本函数
    sqrt: Math.sqrt,
    abs: Math.abs,
    floor: Math.floor,
    ceil: Math.ceil,
    round: Math.round,
    // 对数和指数
    log: Math.log,
    ln: Math.log,
    log10: Math.log10,
    exp: Math.exp,
    pow: Math.pow,
    // 常数
    pi: Math.PI,
    e: Math.E
  }
  
  // 替换数学函数和常量
  let processedExpr = expr
  for (const [name, func] of Object.entries(mathFunctions)) {
    if (typeof func === 'number') {
      // 处理常数
      processedExpr = processedExpr.replace(new RegExp(`\\b${name}\\b`, 'g'), func.toString())
    } else {
      // 处理函数
      const funcPattern = new RegExp(`\\b${name}\\(([^)]+)\\)`, 'g')
      processedExpr = processedExpr.replace(funcPattern, (match, args) => {
        const argValue = evaluateExpression(args)
        return (func as Function)(argValue).toString()
      })
    }
  }
  
  // 处理幂运算（^）
  processedExpr = processedExpr.replace(/([0-9.]+|\([^)]+\))\^([0-9.]+|\([^)]+\))/g, 
    (match, base, exponent) => {
      const baseValue = base.startsWith('(') ? evaluateExpression(base.slice(1, -1)) : parseFloat(base)
      const expValue = exponent.startsWith('(') ? evaluateExpression(exponent.slice(1, -1)) : parseFloat(exponent)
      return Math.pow(baseValue, expValue).toString()
    })
  
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
    
    // 保留合理的精度
    return Math.round(result * 1e12) / 1e12
  } catch (error) {
    throw new Error('无法计算表达式')
  }
} 