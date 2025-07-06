import type { ToolExecutor } from '../utils/tools'
import { createParameterSchema } from '../utils/tools'

// 文本处理工具 - 符合OpenAI标准
export const textProcessorTool: ToolExecutor = {
  definition: {
    name: 'text_processor',
    description: '文本处理工具，支持JSON格式化、Base64编码/解码、URL编码/解码、大小写转换等',
    parameters: createParameterSchema({
      action: {
        type: 'string',
        enum: ['json_format', 'json_minify', 'base64_encode', 'base64_decode', 'url_encode', 'url_decode', 'uppercase', 'lowercase', 'title_case', 'trim', 'word_count'],
        description: '处理类型：json_format（JSON格式化）、json_minify（JSON压缩）、base64_encode（Base64编码）、base64_decode（Base64解码）、url_encode（URL编码）、url_decode（URL解码）、uppercase（转大写）、lowercase（转小写）、title_case（标题格式）、trim（去除空格）、word_count（字数统计）'
      },
      text: {
        type: 'string',
        description: '要处理的文本内容'
      }
    }, ['action', 'text'])
  },
  
  async execute(parameters: Record<string, any>): Promise<string> {
    const { action, text } = parameters
    
    if (!text && text !== '') {
      return '❌ 错误：需要提供text参数'
    }
    
    try {
      switch (action) {
        case 'json_format':
          try {
            const parsed = JSON.parse(text)
            const formatted = JSON.stringify(parsed, null, 2)
            return `✅ JSON格式化完成：\n\`\`\`json\n${formatted}\n\`\`\``
          } catch (error) {
            return '❌ 错误：无效的JSON格式'
          }
          
        case 'json_minify':
          try {
            const parsed = JSON.parse(text)
            const minified = JSON.stringify(parsed)
            return `✅ JSON压缩完成：\n${minified}`
          } catch (error) {
            return '❌ 错误：无效的JSON格式'
          }
          
        case 'base64_encode':
          try {
            const encoded = btoa(unescape(encodeURIComponent(text)))
            return `✅ Base64编码完成：\n${encoded}`
          } catch (error) {
            return '❌ Base64编码失败：包含无效字符'
          }
          
        case 'base64_decode':
          try {
            const decoded = decodeURIComponent(escape(atob(text)))
            return `✅ Base64解码完成：\n${decoded}`
          } catch (error) {
            return '❌ Base64解码失败：无效的Base64字符串'
          }
          
        case 'url_encode':
          const urlEncoded = encodeURIComponent(text)
          return `✅ URL编码完成：\n${urlEncoded}`
          
        case 'url_decode':
          try {
            const urlDecoded = decodeURIComponent(text)
            return `✅ URL解码完成：\n${urlDecoded}`
          } catch (error) {
            return '❌ URL解码失败：无效的URL编码字符串'
          }
          
        case 'uppercase':
          return `✅ 转换为大写：\n${text.toUpperCase()}`
          
        case 'lowercase':
          return `✅ 转换为小写：\n${text.toLowerCase()}`
          
        case 'title_case':
          const titleCase = text.replace(/\w\S*/g, (txt: string) => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
          )
          return `✅ 转换为标题格式：\n${titleCase}`
          
        case 'trim':
          const trimmed = text.trim()
          return `✅ 去除首尾空格：\n"${trimmed}"`
          
        case 'word_count':
          const words = text.trim().split(/\s+/).filter((word: string) => word.length > 0)
          const chars = text.length
          const charsNoSpaces = text.replace(/\s/g, '').length
          const lines = text.split('\n').length
          
          return `📊 文本统计：
🔤 字符数：${chars}
🔤 字符数（不含空格）：${charsNoSpaces}
📝 单词数：${words.length}
📄 行数：${lines}
🔗 段落数：${text.split(/\n\s*\n/).filter((p: string) => p.trim().length > 0).length}`
          
        default:
          return '❌ 错误：无效的处理类型'
      }
    } catch (error) {
      return `❌ 文本处理失败：${error instanceof Error ? error.message : '未知错误'}`
    }
  },
  
  isEnabled: () => true
} 