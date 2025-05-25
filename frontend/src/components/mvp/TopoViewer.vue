<template>
  <div class="h-full bg-white rounded-lg shadow-sm border flex flex-col">
    <!-- 載入中狀態 -->
    <div v-if="isLoading" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600 text-lg">正在載入數據...</p>
        <p class="text-gray-500 text-sm mt-2">請稍候</p>
      </div>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="h-full flex items-center justify-center">
      <div class="text-center text-red-600 max-w-md">
        <svg class="mx-auto h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <p class="text-lg font-medium mb-2">載入失敗</p>
        <p class="text-sm">{{ error }}</p>
      </div>
    </div>

    <!-- 無數據狀態 -->
    <div v-else-if="!currentData" class="h-full flex items-center justify-center">
      <div class="text-center text-gray-500">
        <svg class="mx-auto h-20 w-20 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-xl font-medium mb-2">SPM 形貌圖顯示器</p>
        <p class="text-sm">請載入檔案以顯示形貌圖</p>
      </div>
    </div>

    <!-- 圖像顯示區 -->
    <div v-else class="h-full flex flex-col">
      <!-- 標題欄 -->
      <header class="px-4 py-3 border-b bg-gray-50 flex-shrink-0">
        <div class="flex items-center justify-between">
          <h3 class="font-medium text-gray-800">{{ currentData.name }}</h3>
          <div class="text-sm text-gray-600">
            色彩映射: {{ currentData.colormap }}
          </div>
        </div>
      </header>

      <!-- Plotly 圖表容器 -->
      <div class="flex-1 p-4 min-h-0">
        <div ref="plotlyContainer" class="w-full h-full min-h-[400px]"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Plotly from 'plotly.js-dist-min'
import mvpStore from '../../stores/mvpStore'

// Refs
const plotlyContainer = ref<HTMLElement | null>(null)
let plotlyInstance: any = null

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)
const error = computed(() => mvpStore.error)

// 監聽數據變化
watch(currentData, async (newData) => {
  if (newData && newData.plotlyConfig) {
    await nextTick()
    await createPlotlyChart(newData.plotlyConfig)
  }
}, { immediate: true })

// 監聽 colormap 變化
watch(() => currentData.value?.colormap, async (newColormap, oldColormap) => {
  if (newColormap && newColormap !== oldColormap && currentData.value) {
    console.log('MVP TopoViewer: 色彩映射變更為:', newColormap)
    await updateColormap(newColormap)
  }
})

// 創建 Plotly 圖表（直接使用後端配置）
async function createPlotlyChart(plotlyConfig: any) {
  if (!plotlyContainer.value) {
    console.warn('MVP TopoViewer: plotlyContainer 不存在')
    return
  }

  try {
    console.log('MVP TopoViewer: 開始創建 Plotly 圖表')
    
    // 清除舊圖表
    if (plotlyInstance) {
      Plotly.purge(plotlyContainer.value)
      plotlyInstance = null
    }

    const { data, layout, config } = plotlyConfig

    // 直接使用後端生成的配置創建圖表
    await Plotly.newPlot(plotlyContainer.value, data, layout, config)
    plotlyInstance = plotlyContainer.value

    console.log('MVP TopoViewer: Plotly 圖表創建成功')
  } catch (error) {
    console.error('MVP TopoViewer: 創建 Plotly 圖表失敗:', error)
    mvpStore.setError('創建圖表時發生錯誤: ' + error)
  }
}

// 更新色彩映射（通過後端）
async function updateColormap(newColormap: string) {
  if (!currentData.value) return

  try {
    console.log('MVP TopoViewer: 請求更新色彩映射:', newColormap)
    
    // 調用後端 API 更新色彩映射
    const result = await window.pywebview.api.update_colormap(
      currentData.value.txtFile,
      currentData.value.intFile,
      newColormap
    )

    if (result.success) {
      // 使用新的 Plotly 配置重新創建圖表
      await createPlotlyChart(result.plotlyConfig)
      console.log('MVP TopoViewer: 色彩映射更新成功')
    } else {
      throw new Error(result.error || '更新色彩映射失敗')
    }
  } catch (error) {
    console.error('MVP TopoViewer: 更新色彩映射失敗:', error)
    mvpStore.setError('更新色彩映射失敗: ' + error)
  }
}

// 組件卸載時清理
onBeforeUnmount(() => {
  if (plotlyInstance) {
    console.log('MVP TopoViewer: 清理 Plotly 實例')
    Plotly.purge(plotlyInstance)
    plotlyInstance = null
  }
})
</script>