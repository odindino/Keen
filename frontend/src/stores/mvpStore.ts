// stores/mvpStore.ts
import { reactive } from 'vue'

export interface SPMData {
  id: string
  name: string
  txtFile: string
  intFile?: string
  datFile?: string
  fileType?: string
  plotlyConfig: any  // 新增：Plotly 配置（data + layout + config）
  colormap: string
  dimensions: {
    width: number
    height: number
    xRange: number
    yRange: number
  }
  physUnit: string
  statistics?: {
    min: number
    max: number
    mean: number
    rms: number
  }
  cits_data?: any
  sts_data?: any
}

// 文件選擇相關介面
export interface FileInfo {
  filename: string
  type: 'int' | 'dat'
  caption: string
  file_type?: string
  scale?: number
  phys_unit?: string
  offset?: number
  measurement_mode?: string
  measurement_type?: string
  grid_size?: string
}

export interface TxtFileInfo {
  txt_path: string
  experiment_info: any
  available_files: FileInfo[]
}

// 高度剖面相關介面
export interface ProfilePoint {
  x: number
  y: number
}

export interface ProfileData {
  distance: number[]
  height: number[]
  length: number  // 新增：剖面總長度
  startPoint: ProfilePoint
  endPoint: ProfilePoint
  isPreview?: boolean  // 新增：標記是否為預覽數據
  stats?: {
    min: number
    max: number
    mean: number
    median: number
    std: number  // 新增：標準差
    range: number
    rms: number  // 新增：均方根
  }
}

// 簡化的響應式狀態管理
export const mvpStore = reactive({
  // 原有狀態
  currentData: null as SPMData | null,
  isLoading: false,
  error: null as string | null,
  
  // 文件選擇相關狀態
  txtFileInfo: null as TxtFileInfo | null,
  isFileSelectionMode: false,
  selectedFileInfo: null as FileInfo | null,
  
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

  // 文件選擇相關方法
  setTxtFileInfo(info: TxtFileInfo | null) {
    this.txtFileInfo = info
    this.isFileSelectionMode = !!info
    this.selectedFileInfo = null
    console.log('MVP Store: 設置 TXT 文件信息:', info ? `${info.available_files.length} 個可用文件` : '清除')
  },

  setSelectedFileInfo(fileInfo: FileInfo | null) {
    this.selectedFileInfo = fileInfo
    console.log('MVP Store: 選擇文件:', fileInfo?.filename || '清除選擇')
  },

  exitFileSelectionMode() {
    this.isFileSelectionMode = false
    this.txtFileInfo = null
    this.selectedFileInfo = null
    console.log('MVP Store: 退出文件選擇模式')
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
    this.profileCurrentPoint = point  // 初始时當前點與起點相同
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
    this.exitFileSelectionMode()
  }
})

// 導出 store 實例
export default mvpStore