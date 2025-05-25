// main.ts - MVP 版本
import { createApp } from 'vue'
import App from './App-mvp.vue'  // 使用 MVP 版本的 App
import './styles.css'

console.log('=== 啟動 SPM 數據分析器 V2 (MVP) ===')

const app = createApp(App)

// 全局錯誤處理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 錯誤:', err)
  console.info('組件實例:', instance)
  console.info('錯誤信息:', info)
  
  // 在開發模式下顯示更詳細的錯誤信息
  if (import.meta.env.DEV) {
    console.error('詳細錯誤堆疊:', err)
  }
}

// 掛載應用
app.mount('#app')

console.log('SPM 分析器 MVP 版本啟動完成')
console.log('版本信息: MVP-1.0.0')
console.log('構建時間:', new Date().toISOString())