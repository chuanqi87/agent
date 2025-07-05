import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// 初始化工具系统
import { toolManager } from './tools'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 在应用启动时初始化工具系统
toolManager.init()

app.mount('#app') 