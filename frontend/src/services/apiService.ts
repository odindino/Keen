// services/apiService.ts
import type { SPMData } from '../stores/mvpStore'

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
      dimensions: {
        width: result.dimensions.width,
        height: result.dimensions.height,
        xRange: result.dimensions.xRange,
        yRange: result.dimensions.yRange
      },
      physUnit: result.physUnit || 'nm',
      statistics: {
        min: result.statistics.min,
        max: result.statistics.max,
        mean: result.statistics.mean,
        rms: result.statistics.rms
      }
    }

    console.log('API Service: SPM 檔案載入成功:', data.name)
    return data
  } catch (error) {
    console.error('API Service: 載入 SPM 檔案失敗:', error)
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
        update_colormap(txtPath: string, intPath: string, colormap: string): Promise<{
          success: boolean
          plotlyConfig?: any  // 更新後的 Plotly 配置
          colormap?: string
          error?: string
        }>
      }
    }
  }
}