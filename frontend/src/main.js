/**
 * Vue 3 应用入口
 * 注册 Pinia、Vue Router、全局样式
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

// 状态管理
app.use(createPinia())

// 路由
app.use(router)

app.mount('#app')
