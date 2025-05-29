// services/apiService.ts
import type { SPMData, TxtFileInfo, FileInfo } from '../stores/mvpStore'

/**
 * 載入 SPM 檔案
 */
export async function loadSPMFile(txtFilePath: string): Promise<SPMData> {
  try {
    console.log('API Service: 載入 SPM 檔案:', txtFilePath)
    
    const result = await window.pywebview.api.load_spm_file(txtFilePath)
    
    if (!result.success) {
      throw new Error(result.error || '載入檔案失敗')
    }

    // 轉換後端數據格式為前端格式
    const data: SPMData = {
      id: generateId(),
      name: result.name || extractFileName(txtFilePath),
      txtFile: txtFilePath,
      intFile: result.intFile,
      plotlyConfig: result.plotlyConfig,  // 新增：Plotly 配置
      colormap: result.colormap || 'Oranges',
      dimensions: result.dimensions || {
        width: 256,
        height: 256,
        xRange: 10.0,
        yRange: 10.0
      },
      physUnit: result.physUnit || 'nm',
      statistics: result.statistics ? {
        min: result.statistics.min,
        max: result.statistics.max,
        mean: result.statistics.mean,
        rms: result.statistics.rms
      } : undefined
    }

    console.log('API Service: SPM 檔案載入成功:', data.name)
    return data
  } catch (error) {
    console.error('API Service: 載入 SPM 檔案失敗:', error)
    throw error
  }
}

/**
 * 載入 TXT 檔案並取得可用檔案清單
 */
export async function loadTxtFile(txtFilePath: string): Promise<TxtFileInfo> {
  try {
    console.log('API Service: 載入 TXT 檔案:', txtFilePath)
    
    const result = await window.pywebview.api.load_txt_file(txtFilePath)
    
    if (!result.success) {
      throw new Error(result.error || '載入 TXT 檔案失敗')
    }

    const txtFileInfo: TxtFileInfo = {
      txt_path: result.txt_path || txtFilePath,
      experiment_info: result.experiment_info || {},
      available_files: result.available_files || []
    }

    console.log('API Service: TXT 檔案載入成功，找到', (result.available_files || []).length, '個可用檔案')
    return txtFileInfo
  } catch (error) {
    console.error('API Service: 載入 TXT 檔案失敗:', error)
    throw error
  }
}

/**
 * 載入用戶選擇的特定檔案
 */
export async function loadSelectedFile(txtFilePath: string, selectedFilename: string): Promise<SPMData> {
  try {
    console.log('API Service: 載入選中檔案:', selectedFilename)
    
    const result = await window.pywebview.api.load_selected_file(txtFilePath, selectedFilename)
    
    if (!result.success) {
      throw new Error(result.error || '載入選中檔案失敗')
    }

    // 轉換後端數據格式為前端格式
    const data: SPMData = {
      id: generateId(),
      name: result.name || extractFileName(selectedFilename),
      txtFile: txtFilePath,
      intFile: result.intFile,
      datFile: result.datFile,
      fileType: result.fileType,
      plotlyConfig: result.plotlyConfig,
      colormap: result.colormap || 'Oranges',
      dimensions: result.dimensions || {
        width: 256,
        height: 256,
        xRange: 10.0,
        yRange: 10.0
      },
      physUnit: result.physUnit || 'nm',
      statistics: result.statistics ? {
        min: result.statistics.min,
        max: result.statistics.max,
        mean: result.statistics.mean,
        rms: result.statistics.rms
      } : undefined,
      cits_data: result.cits_data,
      sts_data: result.sts_data
    }

    console.log('API Service: 選中檔案載入成功:', data.name)
    return data
  } catch (error) {
    console.error('API Service: 載入選中檔案失敗:', error)
    throw error
  }
}

// 工具函數
function generateId(): string {
  return `spm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

function extractFileName(filePath: string): string {
  const parts = filePath.split(/[/\\]/)
  return parts[parts.length - 1] || 'Unknown'
}

// 全域類型定義
declare global {
  interface Window {
    pywebview: {
      api: {
        select_txt_file(): Promise<{
          success: boolean
          filePath?: string
          error?: string
        }>
        load_spm_file(txtPath: string): Promise<{
          success: boolean
          name?: string
          intFile?: string
          txtFile?: string
          plotlyConfig?: any  // Plotly 配置對象
          colormap?: string
          dimensions?: {
            width: number
            height: number
            xRange: number
            yRange: number
          }
          physUnit?: string
          statistics?: {
            min: number
            max: number
            mean: number
            rms: number
          }
          error?: string
        }>
        load_txt_file(txtPath: string): Promise<{
          success: boolean
          txt_path?: string
          experiment_info?: any
          available_files?: FileInfo[]
          error?: string
        }>
        load_selected_file(txtPath: string, selectedFilename: string): Promise<{
          success: boolean
          name?: string
          intFile?: string
          datFile?: string
          txtFile?: string
          fileType?: string
          plotlyConfig?: any
          colormap?: string
          dimensions?: {
            width: number
            height: number
            xRange: number
            yRange: number
          }
          physUnit?: string
          statistics?: {
            min: number
            max: number
            mean: number
            rms: number
          }
          cits_data?: any
          sts_data?: any
          message?: string
          error?: string
        }>
        update_colormap(txtPath: string, intPath: string, colormap: string): Promise<{
          success: boolean
          plotlyConfig?: any  // 更新後的 Plotly 配置
          colormap?: string
          error?: string
        }>
        apply_flatten(method: string): Promise<{
          success: boolean
          plotlyConfig?: any
          statistics?: {
            min: number
            max: number
            mean: number
            rms: number
          }
          error?: string
        }>
        adjust_tilt(direction: string, fineTune: boolean): Promise<{
          success: boolean
          plotlyConfig?: any
          statistics?: {
            min: number
            max: number
            mean: number
            rms: number
          }
          error?: string
        }>
        reset_image_processing(): Promise<{
          success: boolean
          plotlyConfig?: any
          statistics?: {
            min: number
            max: number
            mean: number
            rms: number
          }
          error?: string
        }>
      }
    }
  }
}