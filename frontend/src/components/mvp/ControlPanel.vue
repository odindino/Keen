<template>
  <div class="space-y-6 h-full flex flex-col">
    <!-- 檔案載入區 -->
    <section class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">檔案載入</h2>
      <button 
        @click="handleLoadFile"
        :disabled="isLoading"
        class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        <div class="flex items-center justify-center">
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-if="isLoading">載入中...</span>
          <span v-else>選擇 TXT 檔案</span>
        </div>
      </button>
    </section>

    <!-- 檔案資訊 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">檔案資訊</h2>
      <div class="bg-gray-50 rounded-lg p-4 space-y-3 border">
        <div class="text-sm">
          <span class="font-medium text-gray-600">檔案名稱:</span>
          <span class="ml-2 text-gray-900">{{ currentData.name }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">尺寸:</span>
          <span class="ml-2 text-gray-900">{{ currentData.dimensions.width }} × {{ currentData.dimensions.height }} 像素</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">掃描範圍:</span>
          <span class="ml-2 text-gray-900">{{ formatNumber(currentData.dimensions.xRange) }} × {{ formatNumber(currentData.dimensions.yRange) }} {{ currentData.physUnit }}</span>
        </div>
      </div>
    </section>

    <!-- 色彩映射選擇 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">色彩映射</h2>
      <select 
        :value="currentData.colormap"
        @change="handleColormapChange"
        :disabled="isLoading"
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
      >
        <option value="Oranges">橘色 (Oranges)</option>
        <option value="Blues">藍色 (Blues)</option>
        <option value="Reds">紅色 (Reds)</option>
        <option value="Greens">綠色 (Greens)</option>
        <option value="Purples">紫色 (Purples)</option>
        <option value="Greys">灰色 (Greys)</option>
        <option value="viridis">Viridis</option>
        <option value="plasma">Plasma</option>
        <option value="inferno">Inferno</option>
        <option value="magma">Magma</option>
        <option value="Oranges_r">橘色反轉 (Oranges_r)</option>
        <option value="Blues_r">藍色反轉 (Blues_r)</option>
        <option value="Reds_r">紅色反轉 (Reds_r)</option>
        <option value="Greens_r">綠色反轉 (Greens_r)</option>
      </select>
    </section>

    <!-- 統計資訊 -->
    <section v-if="currentData" class="flex-1 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">統計資訊</h2>
      <div class="bg-gray-50 rounded-lg p-4 space-y-3 border">
        <div class="text-sm">
          <span class="font-medium text-gray-600">最小值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.min) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">最大值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.max) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">平均值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.mean) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">RMS:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.rms) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">範圍:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.max - currentData.statistics.min) }} {{ currentData.physUnit }}</span>
        </div>
      </div>
    </section>

    <!-- 提示信息 -->
    <section v-if="!currentData && !isLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center text-gray-500 py-8">
        <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-lg font-medium mb-2">歡迎使用 SPM 分析器</p>
        <p class="text-sm">請選擇 TXT 檔案開始分析</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import mvpStore from '../../stores/mvpStore'
import { loadSPMFile } from '../../services/apiService'

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)

// 載入檔案
async function handleLoadFile() {
  try {
    mvpStore.setLoading(true)
    mvpStore.setError(null)
    
    console.log('MVP: 開始選擇檔案')
    
    // 使用 pywebview 選擇檔案
    const result = await window.pywebview.api.select_txt_file()
    
    if (result.success) {
      console.log('MVP: 檔案選擇成功，開始載入:', result.filePath)
      
      const data = await loadSPMFile(result.filePath)
      mvpStore.setCurrentData(data)
      
      console.log('MVP: 檔案載入成功:', data.name)
    } else {
      throw new Error(result.error || '檔案選擇失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '載入檔案時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 載入檔案失敗:', err)
  } finally {
    mvpStore.setLoading(false)
  }
}

// 處理色彩映射變更
function handleColormapChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const newColormap = target.value
  
  console.log('MVP: 色彩映射變更為:', newColormap)
  mvpStore.updateColormap(newColormap)
}

// 格式化數字顯示
function formatNumber(value: number): string {
  if (value === undefined || value === null) return 'N/A'
  
  // 根據數值大小選擇適當的小數位數
  if (Math.abs(value) >= 100) {
    return value.toFixed(1)
  } else if (Math.abs(value) >= 1) {
    return value.toFixed(2)
  } else {
    return value.toFixed(3)
  }
}
</script>