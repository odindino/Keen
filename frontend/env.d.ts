/// <reference types="vite/client" />

declare module 'plotly.js-dist-min'

declare global {
  interface Window {
    pywebview: {
      api: {
        select_txt_file(): Promise<{ success: boolean; filePath?: string; error?: string }>
        load_spm_file(txtPath: string): Promise<{ success: boolean; name?: string; intFile?: string; plotlyConfig?: any; colormap?: string; dimensions?: any; physUnit?: string; statistics?: any; error?: string }>
        update_colormap(txtPath: string, intPath: string, colormap: string): Promise<{ success: boolean; plotlyConfig?: any; colormap?: string; error?: string }>
        calculate_height_profile(startPoint: [number, number], endPoint: [number, number]): Promise<{ success: boolean; profile_data?: any; error?: string }>
        apply_flatten(method: string): Promise<{ success: boolean; plotlyConfig?: any; statistics?: any; error?: string }>
        adjust_tilt(direction: string, fineTune: boolean): Promise<{ success: boolean; plotlyConfig?: any; statistics?: any; error?: string }>
        reset_image_processing(): Promise<{ success: boolean; plotlyConfig?: any; statistics?: any; error?: string }>
      }
    }
  }
}
