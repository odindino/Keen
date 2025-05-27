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
const isProfileMode = computed(() => mvpStore.isProfileMode)
const profileStartPoint = computed(() => mvpStore.profileStartPoint)
const profileCurrentPoint = computed(() => mvpStore.profileCurrentPoint)
const profileEndPoint = computed(() => mvpStore.profileEndPoint)

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

// 監聽剖面模式變化
watch(isProfileMode, () => {
  if (!isProfileMode.value) {
    // 退出剖面模式時，清除剖面線並重新繪製圖表
    updatePlotWithProfile()
  }
})

// 監聽剖面點變化
watch([profileStartPoint, profileCurrentPoint, profileEndPoint], () => {
  if (isProfileMode.value) {
    updatePlotWithProfile()
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

    // 設置滑鼠事件處理
    setupEventHandlers()

    console.log('MVP TopoViewer: Plotly 圖表創建成功')
  } catch (error) {
    console.error('MVP TopoViewer: 創建 Plotly 圖表失敗:', error)
    mvpStore.setError('創建圖表時發生錯誤: ' + error)
  }
}

// 更新圖表並添加剖面線
function updatePlotWithProfile() {
  if (!plotlyInstance || !currentData.value) return

  const originalConfig = currentData.value.plotlyConfig
  if (!originalConfig) return

  // 複製原始數據
  const plotData = [...originalConfig.data]

  // 添加剖面線（如果在剖面模式中）
  if (isProfileMode.value && profileStartPoint.value) {
    const start = profileStartPoint.value

    // 如果有終點，繪製固定的剖面線
    if (profileEndPoint.value) {
      const end = profileEndPoint.value
      
      plotData.push({
        x: [start.x, end.x],
        y: [start.y, end.y],
        mode: 'lines+markers',
        type: 'scatter',
        line: {
          color: 'white',
          width: 3
        },
        marker: {
          color: ['red', 'red'],
          size: 8,
          symbol: 'circle'
        },
        name: '高度剖面線',
        showlegend: false,
        hoverinfo: 'skip'
      })
    }
    // 如果有當前點（滑鼠移動中）但沒有終點，繪製臨時剖面線
    else if (profileCurrentPoint.value) {
      const current = profileCurrentPoint.value
      
      plotData.push({
        x: [start.x, current.x],
        y: [start.y, current.y],
        mode: 'lines+markers',
        type: 'scatter',
        line: {
          color: 'white',
          width: 2,
          dash: 'dash'
        },
        marker: {
          color: ['red', 'rgba(255,255,255,0.7)'],
          size: [8, 6],
          symbol: ['circle', 'circle']
        },
        name: '預覽剖面線',
        showlegend: false,
        hoverinfo: 'skip'
      })
    }
  }

  // 更新圖表
  Plotly.react(plotlyInstance, plotData, originalConfig.layout, originalConfig.config)
}

// 設置滑鼠事件處理
function setupEventHandlers() {
  if (!plotlyInstance) return
  
  // 監聽左鍵點擊事件
  plotlyInstance.on('plotly_click', (eventData: any) => {
    if (!isProfileMode.value || !eventData.points || eventData.points.length === 0) return
    
    // 獲取點擊的點的數據座標
    const point = eventData.points[0]
    const x = point.x
    const y = point.y
    
    console.log('MVP TopoViewer: 點擊座標:', { x, y })
    
    // 如果還沒有起點，設置起點
    if (!profileStartPoint.value) {
      mvpStore.setProfileStartPoint({ x, y })
    } 
    // 如果已有起點但沒有終點，設置終點
    else if (!profileEndPoint.value) {
      mvpStore.setProfileEndPoint({ x, y })
      
      // TODO: 這裡可以加入後端 API 呼叫來獲取剖面數據
      console.log('MVP TopoViewer: 剖面線完成，起點:', profileStartPoint.value, '終點:', { x, y })
    }
    // 如果已經有終點，則清除現有數據並設置新的起點
    else {
      mvpStore.resetProfileData()
      mvpStore.setProfileStartPoint({ x, y })
    }
  })
  
  // 監聽滑鼠移動事件
  plotlyInstance.on('plotly_hover', (eventData: any) => {
    if (!isProfileMode.value || !profileStartPoint.value || profileEndPoint.value) return
    if (!eventData.points || eventData.points.length === 0) return
    
    // 獲取當前滑鼠位置的數據座標
    const point = eventData.points[0]
    const x = point.x
    const y = point.y
    
    mvpStore.updateProfileCurrentPoint({ x, y })
  })

  console.log('MVP TopoViewer: 滑鼠事件處理器設置完成')
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