<template>
  <div v-if="showSlider" class="cits-bias-slider">
    <div class="slider-header">
      <h4>CITS 偏壓控制</h4>
      <div class="bias-info">
        <span class="current-bias">{{ currentBias.toFixed(3) }}V</span>
        <span class="bias-range">({{ minBias.toFixed(3) }}V ~ {{ maxBias.toFixed(3) }}V)</span>
      </div>
    </div>
    
    <div class="slider-container">
      <div class="slider-wrapper">
        <input
          type="range"
          :min="0"
          :max="biasCount - 1"
          :value="currentIndex"
          @input="handleSliderChange"
          @change="handleSliderChange"
          class="bias-slider"
          :disabled="isLoading"
        />
        <div class="slider-labels">
          <span class="label-start">{{ minBias.toFixed(2) }}V</span>
          <span class="label-end">{{ maxBias.toFixed(2) }}V</span>
        </div>
      </div>
      
      <div class="slider-controls">
        <button
          @click="previousBias"
          :disabled="currentIndex <= 0 || isLoading"
          class="control-btn"
          title="上一個偏壓"
        >
          ◀
        </button>
        
        <div class="index-display">
          {{ currentIndex + 1 }} / {{ biasCount }}
        </div>
        
        <button
          @click="nextBias"
          :disabled="currentIndex >= biasCount - 1 || isLoading"
          class="control-btn"
          title="下一個偏壓"
        >
          ▶
        </button>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-indicator">
      <span>切換偏壓中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { mvpStore } from '../../stores/mvpStore'
import { switchCitsBias } from '../../services/apiService'

// Props 和 Emits
interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  biasChanged: [biasIndex: number, biasValue: number]
  error: [message: string]
}>()

// Reactive state
const isLoading = ref(false)

// Computed properties
const showSlider = computed(() => {
  const shouldShow = mvpStore.isCitsMode && 
         mvpStore.citsData && 
         mvpStore.citsData.biasCount > 1
  
  return shouldShow
})

const currentIndex = computed(() => {
  return mvpStore.getCitsBiasIndex()
})

const currentBias = computed(() => {
  return mvpStore.getCitsBiasValue()
})

const biasCount = computed(() => {
  return mvpStore.getCitsBiasCount()
})

const minBias = computed(() => {
  const range = mvpStore.getCitsBiasRange()
  return range.min
})

const maxBias = computed(() => {
  const range = mvpStore.getCitsBiasRange()
  return range.max
})

// Methods
async function switchToBias(index: number) {
  if (index === currentIndex.value || isLoading.value || props.disabled) {
    return
  }

  try {
    isLoading.value = true
    mvpStore.setError(null)

    console.log('CITS Slider: 切換到偏壓索引:', index)
    
    // 先在本地更新索引，讓UI保持響應
    mvpStore.updateCitsBiasIndex(index)
    
    // 調用後端 API 切換偏壓
    const updatedData = await switchCitsBias(index)
    
    console.log('CITS Slider: API 返回數據:', updatedData)
    
    // 更新完整數據（現在後端會返回完整的CITS數據）
    mvpStore.setCurrentData(updatedData)
    
    // 發送事件通知父組件
    emit('biasChanged', index, mvpStore.getCitsBiasValue())
    
    console.log('CITS Slider: 偏壓切換成功，當前偏壓:', mvpStore.getCitsBiasValue())
    
  } catch (error) {
    console.error('CITS Slider: 切換偏壓失敗:', error)
    
    const errorMessage = error instanceof Error ? error.message : '切換偏壓失敗'
    mvpStore.setError(errorMessage)
    emit('error', errorMessage)
  } finally {
    isLoading.value = false
  }
}

function handleSliderChange(event: Event) {
  const target = event.target as HTMLInputElement
  const index = parseInt(target.value)
  switchToBias(index)
}

function previousBias() {
  if (currentIndex.value > 0) {
    switchToBias(currentIndex.value - 1)
  }
}

function nextBias() {
  if (currentIndex.value < biasCount.value - 1) {
    switchToBias(currentIndex.value + 1)
  }
}

// 鍵盤快捷鍵支持
function handleKeydown(event: KeyboardEvent) {
  if (!showSlider.value || isLoading.value || props.disabled) return
  
  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      previousBias()
      break
    case 'ArrowRight':
      event.preventDefault()
      nextBias()
      break
  }
}

// 添加鍵盤事件監聽 
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.cits-bias-slider {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  transition: all 0.2s ease;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.slider-header h4 {
  margin: 0;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
}

.bias-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.current-bias {
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.bias-range {
  color: #6c757d;
  font-family: 'Courier New', monospace;
}

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slider-wrapper {
  position: relative;
}

.bias-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e9ecef;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

.bias-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.bias-slider::-webkit-slider-thumb:hover {
  background: #0056b3;
  transform: scale(1.1);
}

.bias-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.bias-slider:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 10px;
  color: #6c757d;
  font-family: 'Courier New', monospace;
}

.slider-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.control-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 28px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover:not(:disabled) {
  background: #495057;
  transform: translateY(-1px);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.index-display {
  background: #e9ecef;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  font-family: 'Courier New', monospace;
  min-width: 60px;
  text-align: center;
}

.loading-indicator {
  text-align: center;
  margin-top: 8px;
  padding: 8px;
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  font-size: 12px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .cits-bias-slider {
    padding: 12px;
  }
  
  .slider-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .bias-info {
    align-self: flex-end;
  }
}
</style>
