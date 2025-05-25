// stores/mvpStore.ts
import { ref, reactive } from 'vue'

export interface SPMData {
  id: string
  name: string
  txtFile: string
  intFile: string
  rawData: number[][]
  colormap: string
  dimensions: {
    width: number
    height: number
    xRange: number
    yRange: number
  }
  physUnit: string
  statistics: {
    min: number
    max: number
    mean: number
    rms: number
  }
}

// 簡化的響應式狀態管理
export const mvpStore = reactive({
  // 狀態
  currentData: null as SPMData | null,
  isLoading: false,
  error: null as string | null,
  
  // 操作方法
  setLoading(loading: boolean) {
    this.isLoading = loading
  },
  
  setError(error: string | null) {
    this.error = error
  },
  
  setCurrentData(data: SPMData | null) {
    this.currentData = data
  },
  
  updateColormap(colormap: string) {
    if (this.currentData) {
      this.currentData.colormap = colormap
    }
  },
  
  clear() {
    this.currentData = null
    this.error = null
    this.isLoading = false
  }
})

// 導出 store 實例
export default mvpStore