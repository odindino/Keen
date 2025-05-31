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
      filename: result.name || extractFileName(txtFilePath),
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

    console.log('API Service: SPM 檔案載入成功:', data.filename)
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
      filename: result.name || extractFileName(selectedFilename),
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

    console.log('API Service: 選中檔案載入成功:', data.filename)
    return data
  } catch (error) {
    console.error('API Service: 載入選中檔案失敗:', error)
    throw error
  }
}

/**
 * 切換 CITS 偏壓
 */
export async function switchCitsBias(biasIndex: number): Promise<SPMData> {
  try {
    console.log('API Service: 切換 CITS 偏壓索引:', biasIndex)
    
    const result = await window.pywebview.api.switch_cits_bias(biasIndex)
    
    if (!result.success) {
      throw new Error(result.error || '切換 CITS 偏壓失敗')
    }

    // 轉換後端數據格式為前端格式  
    const data: SPMData = {
      filename: result.name || 'CITS Data',
      txtFile: result.txtFile || '',
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

    console.log('API Service: CITS 偏壓切換成功，當前偏壓:', result.cits_data?.current_bias)
    return data
  } catch (error) {
    console.error('API Service: 切換 CITS 偏壓失敗:', error)
    throw error
  }
}

/**
 * 取得 CITS 偏壓資訊
 */
export async function getCitsBiasInfo(): Promise<{
  biasValues: number[]
  currentBiasIndex: number
  biasCount: number
  minBias: number
  maxBias: number
  currentBias: number
}> {
  try {
    console.log('API Service: 取得 CITS 偏壓資訊')
    
    const result = await window.pywebview.api.get_cits_bias_info()
    
    if (!result.success) {
      throw new Error(result.error || '取得 CITS 偏壓資訊失敗')
    }

    const biasInfo = {
      biasValues: result.bias_values || [],
      currentBiasIndex: result.current_bias_index || 0,
      biasCount: result.bias_count || 0,
      minBias: result.min_bias || 0,
      maxBias: result.max_bias || 0,
      currentBias: result.current_bias || 0
    }

    console.log('API Service: CITS 偏壓資訊取得成功:', biasInfo)
    return biasInfo
  } catch (error) {
    console.error('API Service: 取得 CITS 偏壓資訊失敗:', error)
    throw error
  }
}

/**
 * 計算 CITS 線段剖面的 STS 光譜數據
 */
export async function calculateCitsLineProfile(
  startPoint: [number, number], 
  endPoint: [number, number], 
  interpolationMethod: string = 'linear'
): Promise<{
  success: boolean
  sts_data?: any
  start_point?: [number, number]
  end_point?: [number, number]
  physical_length?: number
  interpolation_method?: string
  error?: string
}> {
  try {
    console.log('API Service: 計算 CITS 線段剖面:', startPoint, '->', endPoint)
    
    const result = await window.pywebview.api.calculate_cits_line_profile(
      startPoint, 
      endPoint, 
      interpolationMethod
    )
    
    if (!result.success) {
      throw new Error(result.error || '計算 CITS 線段剖面失敗')
    }

    console.log('API Service: CITS 線段剖面計算成功')
    return result
    
  } catch (error) {
    console.error('API Service: 計算 CITS 線段剖面失敗:', error)
    throw error
  }
}

/**
 * 生成 STS Evolution 圖
 */
export async function generateCitsEvolutionPlot(
  stsData: any, 
  colormap: string = 'RdBu_r'
): Promise<{
  success: boolean
  plot_config?: any
  plot_type?: string
  error?: string
}> {
  try {
    console.log('API Service: 生成 STS Evolution 圖')
    
    const result = await window.pywebview.api.generate_cits_evolution_plot(
      stsData, 
      colormap
    )
    
    if (!result.success) {
      throw new Error(result.error || '生成 STS Evolution 圖失敗')
    }

    console.log('API Service: STS Evolution 圖生成成功')
    return result
    
  } catch (error) {
    console.error('API Service: 生成 STS Evolution 圖失敗:', error)
    throw error
  }
}

/**
 * 生成 STS 曲線疊加圖
 */
export async function generateCitsOverlayPlot(
  stsData: any, 
  selectedPositions?: number[], 
  normalize: boolean = false
): Promise<{
  success: boolean
  plot_config?: any
  plot_type?: string
  normalize?: boolean
  selected_positions?: number[]
  error?: string
}> {
  try {
    console.log('API Service: 生成 STS 曲線疊加圖')
    
    const result = await window.pywebview.api.generate_cits_overlay_plot(
      stsData, 
      selectedPositions, 
      normalize
    )
    
    if (!result.success) {
      throw new Error(result.error || '生成 STS 曲線疊加圖失敗')
    }

    console.log('API Service: STS 曲線疊加圖生成成功')
    return result
    
  } catch (error) {
    console.error('API Service: 生成 STS 曲線疊加圖失敗:', error)
    throw error
  }
}

/**
 * 應用能帶對齊
 */
export async function applyCitsEnergyAlignment(
  stsData: any, 
  alignmentMethod: string = 'zero_crossing', 
  referencePosition?: number
): Promise<{
  success: boolean
  energy_shifts?: number[]
  alignment_method?: string
  reference_position?: number
  shift_statistics?: {
    min: number
    max: number
    mean: number
    std: number
  }
  error?: string
}> {
  try {
    console.log('API Service: 應用能帶對齊:', alignmentMethod)
    
    const result = await window.pywebview.api.apply_cits_energy_alignment(
      stsData, 
      alignmentMethod, 
      referencePosition
    )
    
    if (!result.success) {
      throw new Error(result.error || '應用能帶對齊失敗')
    }

    console.log('API Service: 能帶對齊應用成功')
    return result
    
  } catch (error) {
    console.error('API Service: 應用能帶對齊失敗:', error)
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
        switch_cits_bias(biasIndex: number): Promise<{
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
        get_cits_bias_info(): Promise<{
          success: boolean
          bias_values?: number[]
          current_bias_index?: number
          bias_count?: number
          min_bias?: number
          max_bias?: number
          current_bias?: number
          error?: string
        }>
        calculate_cits_line_profile(
          start_point: [number, number], 
          end_point: [number, number], 
          interpolation_method?: string
        ): Promise<{
          success: boolean
          sts_data?: any
          start_point?: [number, number]
          end_point?: [number, number]
          physical_length?: number
          interpolation_method?: string
          error?: string
        }>
        generate_cits_evolution_plot(
          sts_data: any, 
          colormap?: string
        ): Promise<{
          success: boolean
          plot_config?: any
          plot_type?: string
          error?: string
        }>
        generate_cits_overlay_plot(
          sts_data: any, 
          selected_positions?: number[], 
          normalize?: boolean
        ): Promise<{
          success: boolean
          plot_config?: any
          plot_type?: string
          normalize?: boolean
          selected_positions?: number[]
          error?: string
        }>
        apply_cits_energy_alignment(
          sts_data: any, 
          alignment_method?: string, 
          reference_position?: number
        ): Promise<{
          success: boolean
          energy_shifts?: number[]
          alignment_method?: string
          reference_position?: number
          shift_statistics?: {
            min: number
            max: number
            mean: number
            std: number
          }
          error?: string
        }>
      }
    }
  }
}