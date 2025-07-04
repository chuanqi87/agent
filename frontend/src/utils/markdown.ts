import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 简单配置
marked.setOptions({
  gfm: true,
  breaks: true
})

export function renderMarkdown(text: string): string {
  try {
    let html = marked.parse(text) as string
    
    // 手动处理代码高亮
    html = html.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g, (match, lang, code) => {
      if (hljs.getLanguage(lang)) {
        try {
          const highlighted = hljs.highlight(code, { language: lang }).value
          return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
        } catch (err) {
          console.error('Highlight error:', err)
        }
      }
      return match
    })
    
    // 处理没有语言标识的代码块
    html = html.replace(/<pre><code>([\s\S]*?)<\/code><\/pre>/g, (match, code) => {
      if (!code.includes('class="hljs')) {
        try {
          const highlighted = hljs.highlightAuto(code).value
          return `<pre><code class="hljs">${highlighted}</code></pre>`
        } catch (err) {
          console.error('Highlight error:', err)
        }
      }
      return match
    })
    
    return html
  } catch (error) {
    console.error('Markdown parse error:', error)
    return text
  }
} 