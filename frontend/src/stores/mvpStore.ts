// stores/mvpStore.ts
import { reactive } from 'vue'

export interface SPMData {
  id: string
  name: string
  txtFile: string
  intFile: string
  plotlyConfig: any  // 新增：Plotly 配置（data + layout + config）
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

// 高度剖面相關介面
export interface ProfilePoint {
  x: number
  y: number
}

export interface ProfileData {
  distance: number[]
  height: number[]
  startPoint: ProfilePoint
  endPoint: ProfilePoint
  stats?: {
    min: number
    max: number
    mean: number
    range: number
  }
}

// 簡化的響應式狀態管理
export const mvpStore = reactive({
  // 原有狀態
  currentData: null as SPMData | null,
  isLoading: false,
  error: null as string | null,
  
  // 高度剖面相關狀態
  isProfileMode: false,
  profileStartPoint: null as ProfilePoint | null,
  profileCurrentPoint: null as ProfilePoint | null,
  profileEndPoint: null as ProfilePoint | null,
  profileData: null as ProfileData | null,
  
  // 原有操作方法
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

  // 高度剖面相關方法
  toggleProfileMode() {
    this.isProfileMode = !this.isProfileMode
    
    // 切換模式時清除現有剖面相關數據
    this.resetProfileData()
    
    console.log('MVP Store: 高度剖面模式', this.isProfileMode ? '啟動' : '關閉')
  },

  resetProfileData() {
    this.profileStartPoint = null
    this.profileCurrentPoint = null
    this.profileEndPoint = null
    this.profileData = null
    console.log('MVP Store: 重置剖面數據')
  },

  setProfileStartPoint(point: ProfilePoint) {
    this.profileStartPoint = point
    this.profileCurrentPoint = point  // 初始時當前點與起點相同
    this.profileEndPoint = null
    this.profileData = null
    console.log('MVP Store: 設置剖面起點:', point)
  },

  updateProfileCurrentPoint(point: ProfilePoint) {
    if (!this.profileStartPoint || !this.isProfileMode) return
    this.profileCurrentPoint = point
  },

  setProfileEndPoint(point: ProfilePoint) {
    if (!this.profileStartPoint || !this.isProfileMode) return
    
    this.profileEndPoint = point
    console.log('MVP Store: 設置剖面終點:', point)
    
    // TODO: 在這裡可以調用後端 API 來計算剖面數據
    // this.calculateProfileData(this.profileStartPoint, point)
  },

  setProfileData(data: ProfileData) {
    this.profileData = data
    console.log('MVP Store: 設置剖面數據，點數:', data.distance.length)
  },

  clear() {
    this.currentData = null
    this.error = null
    this.isLoading = false
    this.resetProfileData()
    this.isProfileMode = false
  }
})

// 導出 store 實例
export default mvpStore