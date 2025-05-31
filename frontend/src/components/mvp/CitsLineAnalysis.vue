<template>
  <div class="cits-line-analysis">
    <!-- 工具欄 -->
    <div class="toolbar">
      <div class="tool-group">
        <button 
          @click="toggleLineMode"
          :class="{ 'active': mvpStore.isCitsLineMode }"
          class="tool-btn"
          title="線段分析模式"
        >
          <i class="icon-line"></i>
          線段分析
        </button>
        
        <select 
          v-model="interpolationMethod" 
          class="method-select"
          :disabled="!mvpStore.isCitsLineMode"
        >
          <option value="linear">線性插值</option>
          <option value="nearest">最近鄰</option>
          <option value="cubic">三次插值</option>
        </select>
      </div>

      <div class="tool-group" v-if="mvpStore.citsLineProfile">
        <button 
          @click="generateEvolutionPlot"
          :disabled="isGenerating"
          class="analysis-btn"
        >
          STS Evolution
        </button>
        
        <button 
          @click="generateOverlayPlot"
          :disabled="isGenerating"
          class="analysis-btn"
        >
          STS 疊加圖
        </button>
        
        <button 
          @click="applyEnergyAlignment"
          :disabled="isGenerating"
          class="analysis-btn"
        >
          能帶對齊
        </button>
      </div>

      <div class="status-info" v-if="mvpStore.citsLineProfile">
        <span class="info-item">
          長度: {{ mvpStore.citsLineProfile.physicalLength.toFixed(2) }} nm
        </span>
        <span class="info-item">
          點數: {{ mvpStore.citsLineProfile.stsData?.n_positions || 0 }}
        </span>
      </div>
    </div>

    <!-- 線段信息面板 -->
    <div v-if="mvpStore.isCitsLineMode" class="line-info-panel">
      <div class="panel-header">
        <h3>線段分析</h3>
        <button @click="clearLine" class="clear-btn">清除</button>
      </div>
      
      <div class="instruction" v-if="!lineStart && !lineEnd">
        點擊圖像設置起始點，再次點擊設置終點
      </div>
      
      <div class="line-coords" v-if="lineStart || lineEnd">
        <div v-if="lineStart" class="coord-group">
          <label>起始點:</label>
          <span>{{ formatCoord(lineStart) }}</span>
        </div>
        <div v-if="lineEnd" class="coord-group">
          <label>終點:</label>
          <span>{{ formatCoord(lineEnd) }}</span>
        </div>
        <div v-if="lineStart && lineEnd" class="coord-group">
          <label>長度:</label>
          <span>{{ calculateLength().toFixed(2) }} nm</span>
        </div>
      </div>

      <button 
        v-if="lineStart && lineEnd && !mvpStore.citsLineProfile"
        @click="calculateLineProfile"
        :disabled="isCalculating"
        class="calculate-btn"
      >
        {{ isCalculating ? '計算中...' : '計算 STS 剖面' }}
      </button>
    </div>

    <!-- 分析結果面板 -->
    <div v-if="mvpStore.citsAnalysisData" class="analysis-results">
      <div class="result-tabs">
        <button 
          v-for="tab in availableTabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="{ 'active': activeTab === tab.key }"
          class="tab-btn"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Evolution 圖 -->
      <div v-if="activeTab === 'evolution' && mvpStore.citsAnalysisData.evolutionPlot" class="plot-container">
        <div id="evolution-plot" class="plot-area"></div>
      </div>

      <!-- 疊加圖 -->
      <div v-if="activeTab === 'overlay' && mvpStore.citsAnalysisData.overlayPlot" class="plot-container">
        <div class="overlay-controls">
          <label>
            <input type="checkbox" v-model="normalizeOverlay" @change="updateOverlayPlot">
            標準化
          </label>
        </div>
        <div id="overlay-plot" class="plot-area"></div>
      </div>

      <!-- 能帶對齊 -->
      <div v-if="activeTab === 'alignment' && mvpStore.citsAnalysisData.energyAlignment" class="alignment-container">
        <div class="alignment-info">
          <h4>能帶對齊結果</h4>
          <div class="stats">
            <div class="stat-item">
              <label>方法:</label>
              <span>{{ mvpStore.citsAnalysisData.energyAlignment.method }}</span>
            </div>
            <div class="stat-item">
              <label>參考位置:</label>
              <span>{{ mvpStore.citsAnalysisData.energyAlignment.referencePosition }}</span>
            </div>
            <div class="stat-item">
              <label>偏移範圍:</label>
              <span>
                {{ mvpStore.citsAnalysisData.energyAlignment.statistics.min.toFixed(2) }} ~ 
                {{ mvpStore.citsAnalysisData.energyAlignment.statistics.max.toFixed(2) }} mV
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { mvpStore } from '@/stores/mvpStore'
import { 
  calculateCitsLineProfile, 
  generateCitsEvolutionPlot, 
  generateCitsOverlayPlot,
  applyCitsEnergyAlignment 
} from '@/services/apiService'
import Plotly from 'plotly.js-dist-min'

// 響應式數據
const interpolationMethod = ref('linear')
const lineStart = ref<[number, number] | null>(null)
const lineEnd = ref<[number, number] | null>(null)
const isCalculating = ref(false)
const isGenerating = ref(false)
const activeTab = ref('evolution')
const normalizeOverlay = ref(false)

// 事件處理
const emit = defineEmits(['error', 'lineDrawn'])

// 計算屬性
const availableTabs = computed(() => {
  const tabs = []
  if (mvpStore.citsAnalysisData?.evolutionPlot) {
    tabs.push({ key: 'evolution', label: 'STS Evolution' })
  }
  if (mvpStore.citsAnalysisData?.overlayPlot) {
    tabs.push({ key: 'overlay', label: 'STS 疊加圖' })
  }
  if (mvpStore.citsAnalysisData?.energyAlignment) {
    tabs.push({ key: 'alignment', label: '能帶對齊' })
  }
  return tabs
})

// 方法
const toggleLineMode = () => {
  mvpStore.toggleCitsLineMode()
  if (!mvpStore.isCitsLineMode) {
    clearLine()
  }
}

const clearLine = () => {
  lineStart.value = null
  lineEnd.value = null
  mvpStore.setCitsLineProfile(null)
  mvpStore.setCitsAnalysisData(null)
}

const formatCoord = (coord: [number, number]) => {
  return `(${coord[0].toFixed(2)}, ${coord[1].toFixed(2)}) nm`
}

const calculateLength = () => {
  if (!lineStart.value || !lineEnd.value) return 0
  const dx = lineEnd.value[0] - lineStart.value[0]
  const dy = lineEnd.value[1] - lineStart.value[1]
  return Math.sqrt(dx * dx + dy * dy)
}

const calculateLineProfile = async () => {
  if (!lineStart.value || !lineEnd.value) return
  
  try {
    isCalculating.value = true
    console.log('計算 CITS 線段剖面...', lineStart.value, lineEnd.value)
    
    const result = await calculateCitsLineProfile(
      lineStart.value,
      lineEnd.value,
      interpolationMethod.value
    )
    
    if (result.success && result.sts_data) {
      mvpStore.setCitsLineProfile({
        startPoint: { x: lineStart.value[0], y: lineStart.value[1] },
        endPoint: { x: lineEnd.value[0], y: lineEnd.value[1] },
        stsData: result.sts_data,
        physicalLength: result.physical_length || 0,
        interpolationMethod: result.interpolation_method || 'linear',
        isActive: true
      })
      
      console.log('CITS 線段剖面計算完成')
    } else {
      throw new Error(result.error || '計算失敗')
    }
    
  } catch (error) {
    console.error('計算 CITS 線段剖面失敗:', error)
    emit('error', error instanceof Error ? error.message : '計算失敗')
  } finally {
    isCalculating.value = false
  }
}

const generateEvolutionPlot = async () => {
  if (!mvpStore.citsLineProfile) return
  
  try {
    isGenerating.value = true
    console.log('生成 STS Evolution 圖...')
    
    const result = await generateCitsEvolutionPlot(
      { sts_data: mvpStore.citsLineProfile.stsData },
      'RdBu_r'
    )
    
    if (result.success && result.plot_config) {
      mvpStore.updateCitsEvolutionPlot(result.plot_config)
      activeTab.value = 'evolution'
      
      // 渲染圖表
      await nextTick()
      renderEvolutionPlot()
      
      console.log('STS Evolution 圖生成完成')
    } else {
      throw new Error(result.error || '生成失敗')
    }
    
  } catch (error) {
    console.error('生成 STS Evolution 圖失敗:', error)
    emit('error', error instanceof Error ? error.message : '生成失敗')
  } finally {
    isGenerating.value = false
  }
}

const generateOverlayPlot = async () => {
  if (!mvpStore.citsLineProfile) return
  
  try {
    isGenerating.value = true
    console.log('生成 STS 疊加圖...')
    
    const result = await generateCitsOverlayPlot(
      { sts_data: mvpStore.citsLineProfile.stsData },
      undefined, // 自動選擇位置
      normalizeOverlay.value
    )
    
    if (result.success && result.plot_config) {
      mvpStore.updateCitsOverlayPlot(result.plot_config)
      activeTab.value = 'overlay'
      
      // 渲染圖表
      await nextTick()
      renderOverlayPlot()
      
      console.log('STS 疊加圖生成完成')
    } else {
      throw new Error(result.error || '生成失敗')
    }
    
  } catch (error) {
    console.error('生成 STS 疊加圖失敗:', error)
    emit('error', error instanceof Error ? error.message : '生成失敗')
  } finally {
    isGenerating.value = false
  }
}

const applyEnergyAlignment = async () => {
  if (!mvpStore.citsLineProfile) return
  
  try {
    isGenerating.value = true
    console.log('應用能帶對齊...')
    
    const result = await applyCitsEnergyAlignment(
      { sts_data: mvpStore.citsLineProfile.stsData },
      'zero_crossing'
    )
    
    if (result.success) {
      mvpStore.updateCitsEnergyAlignment({
        shifts: result.energy_shifts || [],
        method: result.alignment_method || 'zero_crossing',
        referencePosition: result.reference_position || 0,
        statistics: result.shift_statistics || { min: 0, max: 0, mean: 0, std: 0 }
      })
      activeTab.value = 'alignment'
      
      console.log('能帶對齊完成')
    } else {
      throw new Error(result.error || '對齊失敗')
    }
    
  } catch (error) {
    console.error('應用能帶對齊失敗:', error)
    emit('error', error instanceof Error ? error.message : '對齊失敗')
  } finally {
    isGenerating.value = false
  }
}

const updateOverlayPlot = async () => {
  if (!mvpStore.citsLineProfile) return
  await generateOverlayPlot()
}

const renderEvolutionPlot = () => {
  const plotData = mvpStore.citsAnalysisData?.evolutionPlot
  if (!plotData) return
  
  Plotly.newPlot('evolution-plot', plotData.data, plotData.layout, {
    responsive: true,
    displayModeBar: true
  })
}

const renderOverlayPlot = () => {
  const plotData = mvpStore.citsAnalysisData?.overlayPlot
  if (!plotData) return
  
  Plotly.newPlot('overlay-plot', plotData.data, plotData.layout, {
    responsive: true,
    displayModeBar: true
  })
}

// 監聽點擊事件來設置線段端點
const handlePlotClick = (event: any) => {
  if (!mvpStore.isCitsLineMode) return
  
  const points = event.points
  if (points && points.length > 0) {
    const point = points[0]
    const coord: [number, number] = [point.x, point.y]
    
    if (!lineStart.value) {
      lineStart.value = coord
      console.log('設置起始點:', coord)
    } else if (!lineEnd.value) {
      lineEnd.value = coord
      console.log('設置終點:', coord)
      emit('lineDrawn', { start: lineStart.value, end: lineEnd.value })
    } else {
      // 重新開始
      lineStart.value = coord
      lineEnd.value = null
      mvpStore.setCitsLineProfile(null)
      mvpStore.setCitsAnalysisData(null)
    }
  }
}

// 生命週期
onMounted(() => {
  // 監聽主圖的點擊事件
  const plotElement = document.getElementById('main-plot')
  if (plotElement) {
    plotElement.addEventListener('plotly_click', handlePlotClick)
  }
})

onUnmounted(() => {
  const plotElement = document.getElementById('main-plot')
  if (plotElement) {
    plotElement.removeEventListener('plotly_click', handlePlotClick)
  }
})

// 監聽 tab 變化來重新渲染圖表
watch(activeTab, async (newTab) => {
  await nextTick()
  if (newTab === 'evolution') {
    renderEvolutionPlot()
  } else if (newTab === 'overlay') {
    renderOverlayPlot()
  }
})
</script>

<style scoped>
.cits-line-analysis {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e5e5;
  flex-wrap: wrap;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn, .analysis-btn, .calculate-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover, .analysis-btn:hover, .calculate-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.tool-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.tool-btn:disabled, .analysis-btn:disabled, .calculate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.method-select {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
}

.status-info {
  display: flex;
  gap: 16px;
}

.info-item {
  font-size: 14px;
  color: #666;
}

.line-info-panel {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.clear-btn {
  padding: 4px 8px;
  border: 1px solid #ff4d4f;
  border-radius: 4px;
  background: white;
  color: #ff4d4f;
  cursor: pointer;
  font-size: 12px;
}

.clear-btn:hover {
  background: #ff4d4f;
  color: white;
}

.instruction {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 20px;
}

.line-coords {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.coord-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coord-group label {
  font-weight: 500;
  min-width: 60px;
  color: #333;
}

.calculate-btn {
  width: 100%;
  background: #52c41a;
  color: white;
  border-color: #52c41a;
  margin-top: 12px;
}

.calculate-btn:hover {
  background: #389e0d;
  border-color: #389e0d;
}

.analysis-results {
  margin-top: 16px;
}

.result-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-bottom: none;
  background: #f8f9fa;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #e6f7ff;
}

.tab-btn.active {
  background: white;
  border-color: #1890ff;
  color: #1890ff;
}

.plot-container {
  border: 1px solid #d9d9d9;
  border-radius: 0 4px 4px 4px;
  padding: 16px;
  background: white;
}

.plot-area {
  min-height: 400px;
  width: 100%;
}

.overlay-controls {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e5e5;
}

.overlay-controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.alignment-container {
  border: 1px solid #d9d9d9;
  border-radius: 0 4px 4px 4px;
  padding: 16px;
  background: white;
}

.alignment-info h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item label {
  font-weight: 500;
  min-width: 80px;
  color: #333;
}

.icon-line::before {
  content: "📏";
}
</style>
