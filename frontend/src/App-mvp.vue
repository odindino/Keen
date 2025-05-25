<template>
  <div id="app" class="h-screen flex flex-col bg-gray-50">
    <!-- 標題列 -->
    <header class="bg-white shadow-sm border-b flex-shrink-0">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-800">SPM 數據分析器 V2 (MVP)</h1>
          <div class="flex items-center space-x-4">
            <div v-if="currentData" class="text-sm text-gray-600">
              已載入: {{ currentData.name }}
            </div>
            <div class="text-xs text-gray-500 bg-blue-100 px-2 py-1 rounded">
              MVP 版本
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要內容區 -->
    <main class="flex-1 flex overflow-hidden">
      <!-- 左側控制面板 -->
      <aside class="w-80 bg-white border-r shadow-sm flex-shrink-0">
        <div class="h-full p-4">
          <ControlPanel />
        </div>
      </aside>

      <!-- 右側圖像顯示區 -->
      <section class="flex-1 p-4 min-w-0">
        <TopoViewer />
      </section>
    </main>

    <!-- 錯誤提示 (全局) -->
    <div 
      v-if="error" 
      class="fixed bottom-4 right-4 max-w-md bg-red-500 text-white p-4 rounded-lg shadow-lg z-50"
    >
      <div class="flex items-start">
        <svg class="flex-shrink-0 h-5 w-5 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <div class="flex-1">
          <p class="font-medium">發生錯誤</p>
          <p class="text-sm mt-1">{{ error }}</p>
        </div>
        <button 
          @click="clearError" 
          class="flex-shrink-0 ml-3 text-red-200 hover:text-white focus:outline-none"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 載入遮罩 (全局) -->
    <div 
      v-if="isLoading" 
      class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-40"
    >
      <div class="bg-white rounded-lg p-6 shadow-xl">
        <div class="flex items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div>
          <span class="text-gray-700">處理中，請稍候...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ControlPanel from './components/mvp/ControlPanel.vue'
import TopoViewer from './components/mvp/TopoViewer.vue'
import mvpStore from './stores/mvpStore'

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)
const error = computed(() => mvpStore.error)

// 清除錯誤
function clearError() {
  mvpStore.setError(null)
}

// 在控制台輸出 MVP 啟動信息
console.log('=== SPM 數據分析器 V2 (MVP) 啟動 ===')
console.log('版本: MVP')
console.log('建構日期:', new Date().toISOString())
console.log('功能: 基本檔案載入、形貌圖顯示、色彩映射變更')
console.log('========================================')
</script>

<style>
#app {
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 確保不會產生水平滾動條 */
html, body {
  overflow-x: hidden;
}

/* 自定義滾動條樣式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>