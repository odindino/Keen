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

    <!-- 色彩映射選擇 - 增強版本 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">色彩映射</h2>
      <div class="space-y-4">
        <!-- 當前選擇顯示 -->
        <div class="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
          <div class="flex items-center justify-between">
            <span>當前: <span class="font-medium text-blue-700">{{ getCurrentColormapDisplay() }}</span></span>
            <span v-if="isReversed" class="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">反轉</span>
          </div>
        </div>
        
        <!-- 色彩映射選擇器 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">選擇色彩映射</label>
          <select 
            v-model="selectedColormap"
            @change="updateColormapFromSelection"
            :disabled="isLoading || colormapUpdating"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 disabled:bg-gray-100"
          >
            <!-- 單色系 -->
            <optgroup label="單色系">
              <option value="Oranges">橘色 (Oranges)</option>
              <option value="Blues">藍色 (Blues)</option>
              <option value="Reds">紅色 (Reds)</option>
              <option value="Greens">綠色 (Greens)</option>
              <option value="Purples">紫色 (Purples)</option>
              <option value="Greys">灰階 (Greys)</option>
            </optgroup>
            
            <!-- 科學可視化 -->
            <optgroup label="科學可視化">
              <option value="Viridis">Viridis</option>
              <option value="Plasma">Plasma</option>
              <option value="Inferno">Inferno</option>
              <option value="Magma">Magma</option>
              <option value="Cividis">Cividis</option>
            </optgroup>
            
            <!-- 分歧色彩映射 -->
            <optgroup label="分歧色彩映射">
              <option value="RdYlBu">紅-黃-藍 (RdYlBu)</option>
              <option value="RdYlGn">紅-黃-綠 (RdYlGn)</option>
              <option value="Spectral">光譜 (Spectral)</option>
              <option value="Coolwarm">冷-暖 (Coolwarm)</option>
            </optgroup>
            
            <!-- 彩虹和經典 -->
            <optgroup label="彩虹和經典">
              <option value="Rainbow">彩虹 (Rainbow)</option>
              <option value="Jet">Jet</option>
              <option value="Hot">熱色 (Hot)</option>
              <option value="Cool">冷色 (Cool)</option>
            </optgroup>
            
            <!-- 地形和其他 -->
            <optgroup label="地形和其他">
              <option value="Terrain">地形 (Terrain)</option>
              <option value="Ocean">海洋 (Ocean)</option>
              <option value="Copper">銅色 (Copper)</option>
            </optgroup>
          </select>
        </div>
        
        <!-- 反轉選擇框 -->
        <div>
          <label class="flex items-center space-x-3 cursor-pointer">
            <input 
              type="checkbox" 
              v-model="isReversed"
              @change="updateColormapFromSelection"
              :disabled="isLoading || colormapUpdating"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
            >
            <span class="text-sm font-medium text-gray-700">反轉色彩映射</span>
          </label>
          <p class="text-xs text-gray-500 mt-1 ml-7">勾選後會反轉顏色順序</p>
        </div>
        
        <!-- 更新狀態指示 -->
        <div v-if="colormapUpdating" class="text-sm text-blue-600 flex items-center bg-blue-50 p-3 rounded-lg">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          正在更新色彩映射...
        </div>
      </div>
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
import { ref, computed, watch } from 'vue'
import mvpStore from '../../stores/mvpStore'
import { loadSPMFile } from '../../services/apiService'

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)

// 色彩映射控制狀態
const colormapUpdating = ref(false)
const selectedColormap = ref('Oranges')
const isReversed = ref(false)

// 監聽當前數據變化，同步 UI 狀態
watch(currentData, (newData) => {
  if (newData) {
    // 解析當前的 colormap
    const currentColormap = newData.colormap
    if (currentColormap.endsWith('_r')) {
      selectedColormap.value = currentColormap.slice(0, -2)
      isReversed.value = true
    } else {
      selectedColormap.value = currentColormap
      isReversed.value = false
    }
  }
})

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
      console.log('MVP: 預設色彩映射:', data.colormap)
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

// 從選擇器更新色彩映射
async function updateColormapFromSelection() {
  if (!currentData.value) return
  
  // 構建新的 colormap 名稱
  const newColormap = isReversed.value ? `${selectedColormap.value}_r` : selectedColormap.value
  
  if (newColormap === currentData.value.colormap) {
    return // 沒有變化
  }
  
  try {
    colormapUpdating.value = true
    console.log('MVP: 開始更新色彩映射為:', newColormap)
    
    // 調用後端 API 更新色彩映射
    const result = await window.pywebview.api.update_colormap(
      currentData.value.txtFile,
      currentData.value.intFile,
      newColormap
    )
    
    if (result.success) {
      // 更新 store 中的色彩映射和 plotly 配置
      mvpStore.updateColormap(newColormap)
      if (currentData.value) {
        currentData.value.plotlyConfig = result.plotlyConfig
      }
      
      console.log('MVP: 色彩映射更新成功:', newColormap)
    } else {
      throw new Error(result.error || '更新色彩映射失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '更新色彩映射時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 更新色彩映射失敗:', err)
    
    // 恢復到之前的狀態
    if (currentData.value) {
      const currentColormap = currentData.value.colormap
      if (currentColormap.endsWith('_r')) {
        selectedColormap.value = currentColormap.slice(0, -2)
        isReversed.value = true
      } else {
        selectedColormap.value = currentColormap
        isReversed.value = false
      }
    }
  } finally {
    colormapUpdating.value = false
  }
}

// 獲取當前色彩映射的顯示名稱
function getCurrentColormapDisplay(): string {
  if (!currentData.value) return ''
  
  const colormap = currentData.value.colormap
  
  // 色彩映射顯示名稱映射
  const displayNames: Record<string, string> = {
    'Oranges': '橘色',
    'Blues': '藍色',
    'Reds': '紅色',
    'Greens': '綠色',
    'Purples': '紫色',
    'Greys': '灰階',
    'Viridis': 'Viridis',
    'Plasma': 'Plasma',
    'Inferno': 'Inferno',
    'Magma': 'Magma',
    'Cividis': 'Cividis',
    'RdYlBu': '紅-黃-藍',
    'RdYlGn': '紅-黃-綠',
    'Spectral': '光譜',
    'Coolwarm': '冷-暖',
    'Rainbow': '彩虹',
    'Jet': 'Jet',
    'Hot': '熱色',
    'Cool': '冷色',
    'Terrain': '地形',
    'Ocean': '海洋',
    'Copper': '銅色'
  }
  
  if (colormap.endsWith('_r')) {
    const baseName = colormap.slice(0, -2)
    return `${displayNames[baseName] || baseName} (反轉)`
  }
  
  return displayNames[colormap] || colormap
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