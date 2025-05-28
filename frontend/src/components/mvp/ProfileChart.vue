<template>
  <div class="h-full bg-white rounded-lg shadow-sm border flex flex-col">
    <!-- 標題欄 -->
    <div class="p-3 border-b bg-gray-50 flex-shrink-0">
      <h3 class="text-lg font-semibold text-gray-800">高度剖面圖表</h3>
    </div>
    
    <!-- 無數據狀態 -->
    <div v-if="!profileData" class="flex-1 flex items-center justify-center">
      <div class="text-center text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p class="text-sm font-medium mb-1">尚無剖面數據</p>
        <p class="text-xs text-gray-400">請在圖像上拉線以顯示剖面</p>
      </div>
    </div>
    
    <!-- 剖面圖表 -->
    <div v-else class="flex-1 p-4 min-h-0">
      <div ref="chartContainer" class="w-full h-full"></div>
    </div>
    
    <!-- 統計資訊 -->
    <div v-if="profileData && profileData.stats" class="flex-shrink-0 p-3 border-t bg-gray-50">
      <div class="grid grid-cols-3 gap-4 text-sm">
        <div>
          <span class="font-medium text-gray-600">總長度:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.length) }} nm</span>
        </div>
        <div>
          <span class="font-medium text-gray-600">最小值:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.stats.min) }} nm</span>
        </div>
        <div>
          <span class="font-medium text-gray-600">最大值:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.stats.max) }} nm</span>
        </div>
        <div>
          <span class="font-medium text-gray-600">平均值:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.stats.mean) }} nm</span>
        </div>
        <div>
          <span class="font-medium text-gray-600">範圍:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.stats.range) }} nm</span>
        </div>
        <div>
          <span class="font-medium text-gray-600">標準差:</span>
          <span class="ml-1 text-gray-900 font-mono">{{ formatNumber(profileData.stats.std) }} nm</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import Plotly from 'plotly.js-dist-min'
import mvpStore from '../../stores/mvpStore'

const chartContainer = ref<HTMLElement | null>(null)
let plotlyInstance: any = null

// 從 store 獲取剖面數據
const profileData = computed(() => mvpStore.profileData)
const currentData = computed(() => mvpStore.currentData)

// 創建剖面圖表
async function createProfileChart(data: any) {
  if (!chartContainer.value || !data) return

  try {
    console.log('ProfileChart: 開始創建剖面圖表')
    
    // 清除舊圖表
    if (plotlyInstance) {
      Plotly.purge(chartContainer.value)
      plotlyInstance = null
    }

    // 根據是否為預覽數據調整視覺樣式
    const isPreview = data.isPreview || false

    console.log('ProfileChart: 距離數據:', data.distance)
    console.log('ProfileChart: 高度數據:', data.height)
    console.log('ProfileChart: 剖面總長度:', data.length, 'nm')

    const plotData = [{
      x: data.distance,  // 直接使用原始距離數據
      y: data.height,
      type: 'scatter',
      mode: 'lines',  // 移除 markers，只保留線條
      line: { 
        color: '#3B82F6',  // 統一使用藍色
        width: 2.5,
        shape: 'spline',
        smoothing: 1.3,
        dash: 'solid'  // 統一使用實線
      },
      name: isPreview ? '預覽剖面' : '高度剖面',
      hoverinfo: 'x+y',
      hoverlabel: {
        bgcolor: '#F8FAFC',
        bordercolor: '#3B82F6',
        font: { color: '#1E3A8A' }
      }
    }]

    const layout = {
      title: {
        text: isPreview ? '高度剖面 (預覽)' : `高度剖面 (總長度: ${formatNumber(data.length)} nm)`,
        font: { size: 16 }
      },
      xaxis: { 
        title: '距離 (nm)',
        showgrid: true,
        gridcolor: '#f0f0f0',
        autorange: false,  // 改為固定範圍
        range: [0, data.length] // 確保顯示從0到總長度
      },
      yaxis: { 
        title: '高度 (nm)',
        showgrid: true,
        gridcolor: '#f0f0f0',
        autorange: true
      },
      margin: { l: 65, r: 25, t: 50, b: 65 },
      showlegend: false,
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      hovermode: 'x unified',
      // 自適應容器大小
      autosize: true,
      // 確保圖表高度足夠顯示細節，但不會太佔空間
      height: 500,
      // 增加圖表的交互性設置
      dragmode: 'zoom',
      modebar: {
        orientation: 'v'
      }
    }

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    }

    await Plotly.newPlot(chartContainer.value, plotData, layout, config)
    plotlyInstance = chartContainer.value
    
    console.log('ProfileChart: 剖面圖表創建成功')
  } catch (error) {
    console.error('ProfileChart: 創建剖面圖表失敗:', error)
  }
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

// 監聽剖面數據變化
watch(profileData, async (newData) => {
  if (newData) {
    await nextTick()
    await createProfileChart(newData)
  }
}, { immediate: true })

// 組件掛載時初始化
onMounted(async () => {
  if (profileData.value) {
    await nextTick()
    await createProfileChart(profileData.value)
  }
})

// 組件卸載時清理
onBeforeUnmount(() => {
  if (plotlyInstance) {
    console.log('ProfileChart: 清理 Plotly 實例')
    Plotly.purge(plotlyInstance)
    plotlyInstance = null
  }
})
</script>
