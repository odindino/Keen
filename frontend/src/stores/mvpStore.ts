// stores/mvpStore.ts
import { reactive } from 'vue'

export interface SPMData {
  filename: string
  txtFile: string
  intFile?: string
  datFile?: string
  fileType?: string
  plotlyConfig: any
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
  cits_data?: {
    bias_values: number[]
    current_bias_index: number
    current_bias: number
    bias_count: number
    min_bias: number
    max_bias: number
    measurement_type: string
    grid_size: number[]
  }
  sts_data?: any
}

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

export interface ProfilePoint {
  x: number
  y: number
}

export interface ProfileData {
  distance: number[]
  height: number[]
  length: number
  startPoint: ProfilePoint
  endPoint: ProfilePoint
  isPreview?: boolean
  stats?: {
    min: number
    max: number
    mean: number
    median: number
    std: number
    range: number
    rms: number
  }
}

export interface CitsBiasInfo {
  biasValues: number[]
  currentBiasIndex: number
  biasCount: number
  minBias: number
  maxBias: number
  currentBias: number
}

export interface CitsLineProfile {
  startPoint: ProfilePoint
  endPoint: ProfilePoint
  stsData: any
  physicalLength: number
  interpolationMethod: string
  isActive: boolean
}

export interface CitsAnalysisData {
  evolutionPlot?: any
  overlayPlot?: any
  energyAlignment?: {
    shifts: number[]
    method: string
    referencePosition: number
    statistics: {
      min: number
      max: number
      mean: number
      std: number
    }
  }
}

export const mvpStore = reactive({
  currentData: null as SPMData | null,
  isLoading: false,
  error: null as string | null,
  
  txtFileInfo: null as TxtFileInfo | null,
  isFileSelectionMode: false,
  selectedFileInfo: null as FileInfo | null,
  
  isProfileMode: false,
  profileStartPoint: null as ProfilePoint | null,
  profileCurrentPoint: null as ProfilePoint | null,
  profileEndPoint: null as ProfilePoint | null,
  profileData: null as ProfileData | null,
  
  citsData: null as CitsBiasInfo | null,
  isCitsMode: false,
  
  // CITS 線段分析相關狀態
  isCitsLineMode: false,
  citsLineProfile: null as CitsLineProfile | null,
  citsAnalysisData: null as CitsAnalysisData | null,
  
  setLoading(loading: boolean) {
    this.isLoading = loading
  },
  
  setError(error: string | null) {
    this.error = error
  },
  
  setCurrentData(data: SPMData | null) {
    this.currentData = data
    
    if (data?.cits_data) {
      this.setCitsData({
        biasValues: data.cits_data.bias_values,
        currentBiasIndex: data.cits_data.current_bias_index,
        biasCount: data.cits_data.bias_count,
        minBias: data.cits_data.min_bias,
        maxBias: data.cits_data.max_bias,
        currentBias: data.cits_data.current_bias
      })
      this.isCitsMode = true
    } else if (!this.isCitsMode) {
      // 只有當前不在CITS模式時才清除CITS數據
      // 這樣可以防止在CITS偏壓切換過程中意外清除CITS狀態
      this.citsData = null
      this.isCitsMode = false
    }
  },

  // 新增：專門用於更新當前數據但保持CITS狀態的方法
  updateCurrentDataKeepCits(data: SPMData | null) {
    if (data && this.currentData) {
      // 只更新基本屬性，保持CITS狀態不變
      this.currentData.plotlyConfig = data.plotlyConfig
      this.currentData.statistics = data.statistics
      this.currentData.colormap = data.colormap
      if (data.dimensions) {
        this.currentData.dimensions = data.dimensions
      }
    } else {
      this.setCurrentData(data)
    }
  },
  
  updateColormap(colormap: string) {
    if (this.currentData) {
      this.currentData.colormap = colormap
    }
  },

  setTxtFileInfo(info: TxtFileInfo | null) {
    this.txtFileInfo = info
    this.isFileSelectionMode = !!info
    this.selectedFileInfo = null
  },

  setSelectedFileInfo(fileInfo: FileInfo | null) {
    this.selectedFileInfo = fileInfo
  },

  exitFileSelectionMode() {
    this.isFileSelectionMode = false
    this.txtFileInfo = null
    this.selectedFileInfo = null
  },

  toggleProfileMode() {
    this.isProfileMode = !this.isProfileMode
    this.resetProfileData()
  },

  resetProfileData() {
    this.profileStartPoint = null
    this.profileCurrentPoint = null
    this.profileEndPoint = null
    this.profileData = null
  },

  setProfileStartPoint(point: ProfilePoint) {
    this.profileStartPoint = point
    this.profileCurrentPoint = point
    this.profileEndPoint = null
    this.profileData = null
  },

  updateProfileCurrentPoint(point: ProfilePoint) {
    if (!this.profileStartPoint || !this.isProfileMode) return
    this.profileCurrentPoint = point
  },

  setProfileEndPoint(point: ProfilePoint) {
    if (!this.profileStartPoint || !this.isProfileMode) return
    this.profileEndPoint = point
  },

  setProfileData(data: ProfileData) {
    this.profileData = data
  },

  setCitsData(data: CitsBiasInfo | null) {
    this.citsData = data
    this.isCitsMode = !!data
  },

  updateCitsBiasIndex(index: number) {
    if (!this.citsData) return
    
    this.citsData.currentBiasIndex = index
    this.citsData.currentBias = this.citsData.biasValues[index]
    
    if (this.currentData?.cits_data) {
      this.currentData.cits_data.current_bias_index = index
      this.currentData.cits_data.current_bias = this.citsData.currentBias
    }
  },

  getCitsBiasIndex(): number {
    return this.citsData?.currentBiasIndex ?? 0
  },

  getCitsBiasValue(): number {
    return this.citsData?.currentBias ?? 0
  },

  getCitsBiasRange(): { min: number, max: number } {
    return {
      min: this.citsData?.minBias ?? 0,
      max: this.citsData?.maxBias ?? 0
    }
  },

  getCitsBiasCount(): number {
    return this.citsData?.biasCount ?? 0
  },

  clear() {
    this.currentData = null
    this.error = null
    this.isLoading = false
    this.resetProfileData()
    this.isProfileMode = false
    this.exitFileSelectionMode()
    this.setCitsData(null)
    this.resetCitsLineData()
  },

  // CITS 線段分析相關方法
  toggleCitsLineMode() {
    this.isCitsLineMode = !this.isCitsLineMode
    if (!this.isCitsLineMode) {
      this.resetCitsLineData()
    }
  },

  resetCitsLineData() {
    this.isCitsLineMode = false
    this.citsLineProfile = null
    this.citsAnalysisData = null
  },

  setCitsLineProfile(profile: CitsLineProfile | null) {
    this.citsLineProfile = profile
  },

  setCitsAnalysisData(data: CitsAnalysisData | null) {
    this.citsAnalysisData = data
  },

  updateCitsEvolutionPlot(plotConfig: any) {
    if (!this.citsAnalysisData) {
      this.citsAnalysisData = {}
    }
    this.citsAnalysisData.evolutionPlot = plotConfig
  },

  updateCitsOverlayPlot(plotConfig: any) {
    if (!this.citsAnalysisData) {
      this.citsAnalysisData = {}
    }
    this.citsAnalysisData.overlayPlot = plotConfig
  },

  updateCitsEnergyAlignment(alignmentData: any) {
    if (!this.citsAnalysisData) {
      this.citsAnalysisData = {}
    }
    this.citsAnalysisData.energyAlignment = alignmentData
  }
})

export default mvpStore