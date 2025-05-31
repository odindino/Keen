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
          <h3 class="font-medium text-gray-800">{{ currentData.filename }}</h3>
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

// 即時剖面更新的節流控制
let hoverUpdateTimeout: number | null = null

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)
const error = computed(() => mvpStore.error)
const isProfileMode = computed(() => mvpStore.isProfileMode)
const profileStartPoint = computed(() => mvpStore.profileStartPoint)
const profileCurrentPoint = computed(() => mvpStore.profileCurrentPoint)
const profileEndPoint = computed(() => mvpStore.profileEndPoint)

// CITS 線段分析相關狀態
const isCitsLineMode = computed(() => mvpStore.isCitsLineMode)
const citsLineProfile = computed(() => mvpStore.citsLineProfile)
const isCitsMode = computed(() => mvpStore.isCitsMode)

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

// 監聽 CITS 線段模式變化
watch(isCitsLineMode, () => {
  if (!isCitsLineMode.value) {
    // 退出 CITS 線段模式時，清除線段並重新繪製圖表
    updatePlotWithCitsLine()
  }
})

// 監聽剖面點變化
watch([profileStartPoint, profileCurrentPoint, profileEndPoint], () => {
  if (isProfileMode.value) {
    updatePlotWithProfile()
  }
})

// 監聽 CITS 線段變化
watch([citsLineProfile], () => {
  if (isCitsLineMode.value) {
    updatePlotWithCitsLine()
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

// 更新圖表並添加 CITS 線段
function updatePlotWithCitsLine() {
  if (!plotlyInstance || !currentData.value) return

  const originalConfig = currentData.value.plotlyConfig
  if (!originalConfig) return

  // 複製原始數據
  const plotData = [...originalConfig.data]

  // 添加 CITS 線段（如果在線段模式中）
  if (isCitsLineMode.value && citsLineProfile.value) {
    const profile = citsLineProfile.value
    
    plotData.push({
      x: [profile.startPoint.x, profile.endPoint.x],
      y: [profile.startPoint.y, profile.endPoint.y],
      mode: 'lines+markers',
      type: 'scatter',
      line: {
        color: 'yellow',
        width: 3
      },
      marker: {
        color: ['orange', 'orange'],
        size: 8,
        symbol: 'circle'
      },
      name: 'CITS 線段分析',
      showlegend: false,
      hoverinfo: 'skip'
    })
  }

  // 更新圖表
  Plotly.react(plotlyInstance, plotData, originalConfig.layout, originalConfig.config)
}

// 處理 CITS 線段分析點擊
async function handleCitsLineClick(x: number, y: number) {
  // 如果還沒有起點，設置起點
  if (!citsLineProfile.value) {
    console.log('MVP TopoViewer: 設置 CITS 線段起點:', { x, y })
    mvpStore.setCitsLineProfile({
      startPoint: { x, y },
      endPoint: { x, y },
      stsData: null,
      physicalLength: 0,
      interpolationMethod: 'linear',
      isActive: false
    })
  } 
  // 如果已有起點，設置終點並計算 CITS 線段數據
  else {
    console.log('MVP TopoViewer: 設置 CITS 線段終點:', { x, y })
    
    try {
      console.log('MVP TopoViewer: 開始計算 CITS 線段數據...')
      const api = window.pywebview.api as any
      const result = await api.calculate_cits_line_profile(
        [citsLineProfile.value.startPoint.x, citsLineProfile.value.startPoint.y],
        [x, y],
        'linear' // 默認插值方法
      )
      
      if (result.success) {
        // 更新線段配置
        mvpStore.setCitsLineProfile({
          startPoint: citsLineProfile.value.startPoint,
          endPoint: { x, y },
          stsData: result.profile_data,
          physicalLength: result.profile_data.physical_length,
          interpolationMethod: 'linear',
          isActive: true
        })
        console.log('MVP TopoViewer: CITS 線段計算成功:', result.profile_data)
      } else {
        console.error('MVP TopoViewer: CITS 線段計算失敗:', result.error)
        mvpStore.setError('CITS 線段計算失敗: ' + result.error)
      }
    } catch (error) {
      console.error('MVP TopoViewer: 調用 CITS 線段 API 失敗:', error)
      mvpStore.setError('調用 CITS 線段 API 失敗')
    }
  }
}

// 處理高度剖面點擊
async function handleProfileClick(x: number, y: number) {
  // 如果還沒有起點，設置起點
  if (!profileStartPoint.value) {
    mvpStore.setProfileStartPoint({ x, y })
  } 
  // 如果已有起點但沒有終點，設置終點並計算剖面
  else if (!profileEndPoint.value) {
    mvpStore.setProfileEndPoint({ x, y })
    
    // 調用後端 API 計算剖面數據
    try {
      console.log('MVP TopoViewer: 開始計算剖面數據...')
      const api = window.pywebview.api as any
      const result = await api.calculate_height_profile(
        [profileStartPoint.value.x, profileStartPoint.value.y],
        [x, y]
      )
      
      if (result.success) {
        // 最終確認的剖面，清除預覽標記，並添加起點終點資訊
        const finalData = { 
          ...result.profile_data, 
          isPreview: false,
          startPoint: profileStartPoint.value,
          endPoint: { x, y }
        }
        mvpStore.setProfileData(finalData)
        console.log('MVP TopoViewer: 剖面計算成功:', result.profile_data)
      } else {
        console.error('MVP TopoViewer: 剖面計算失敗:', result.error)
        mvpStore.setError('剖面計算失敗: ' + result.error)
      }
    } catch (error) {
      console.error('MVP TopoViewer: 調用剖面 API 失敗:', error)
      mvpStore.setError('調用剖面 API 失敗')
    }
  }
  // 如果已經有終點，則清除現有數據並設置新的起點
  else {
    mvpStore.resetProfileData()
    mvpStore.setProfileStartPoint({ x, y })
  }
}

// 設置滑鼠事件處理
function setupEventHandlers() {
  if (!plotlyInstance) return
  
  // 監聽左鍵點擊事件
  plotlyInstance.on('plotly_click', async (eventData: any) => {
    if (!eventData.points || eventData.points.length === 0) return
    
    // 獲取點擊的點的數據座標
    const point = eventData.points[0]
    const x = point.x
    const y = point.y
    
    console.log('MVP TopoViewer: 點擊座標:', { x, y })
    
    // 處理 CITS 線段分析模式
    if (isCitsLineMode.value && isCitsMode.value) {
      await handleCitsLineClick(x, y)
      return
    }
    
    // 處理高度剖面模式
    if (isProfileMode.value) {
      await handleProfileClick(x, y)
      return
    }
  })
  
  // 監聽滑鼠移動事件 - 增加即時剖面計算
  plotlyInstance.on('plotly_hover', async (eventData: any) => {
    if (!isProfileMode.value || !profileStartPoint.value || profileEndPoint.value) return
    if (!eventData.points || eventData.points.length === 0) return
    
    // 獲取當前滑鼠位置的數據座標
    const point = eventData.points[0]
    const x = point.x
    const y = point.y
    
    mvpStore.updateProfileCurrentPoint({ x, y })
    
    // 使用節流機制避免過於頻繁的 API 調用
    if (hoverUpdateTimeout) {
      clearTimeout(hoverUpdateTimeout)
    }
    
    hoverUpdateTimeout = setTimeout(async () => {
      try {
        console.log('MVP TopoViewer: 即時計算剖面數據...')
        const api = window.pywebview.api as any;
        const result = await api.calculate_height_profile(
          [profileStartPoint.value!.x, profileStartPoint.value!.y],
          [x, y]
        )
        
        if (result.success) {
          // 標記為預覽數據，並添加起點終點資訊
          const previewData = { 
            ...result.profile_data, 
            isPreview: true,
            startPoint: profileStartPoint.value,
            endPoint: { x, y }
          }
          mvpStore.setProfileData(previewData)
        }
      } catch (error) {
        console.warn('即時剖面計算失敗:', error)
      }
    }, 150) // 150ms 節流
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
      currentData.value.intFile || '',
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
  // 清理節流計時器
  if (hoverUpdateTimeout) {
    clearTimeout(hoverUpdateTimeout)
    hoverUpdateTimeout = null
  }
  
  if (plotlyInstance) {
    console.log('MVP TopoViewer: 清理 Plotly 實例')
    Plotly.purge(plotlyInstance)
    plotlyInstance = null
  }
})
</script>