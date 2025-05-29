<template>
  <div class="h-full flex flex-col">
    <!-- 滾動容器 -->
    <div class="flex-1 overflow-y-auto px-4 py-6 space-y-6">
      <!-- 檔案載入區 -->
      <section class="flex-shrink-0">
        <h2 class="text-lg font-semibold mb-3 text-gray-800">檔案載入</h2>
        <button 
          @click="handleLoadFile"
          :disabled="isLoading"
          class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <div class="flex items-center justify-center">
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-if="isLoading">載入中...</span>
            <span v-else>選擇 TXT 檔案</span>
          </div>
        </button>
      </section>

      <!-- 檔案資訊 -->
      <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">檔案資訊</h2>
      <div class="bg-gray-50 rounded-lg p-4 space-y-3 border">
        <div class="text-sm">
          <span class="font-medium text-gray-600">檔案名稱:</span>
          <span class="ml-2 text-gray-900">{{ currentData.name }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">尺寸:</span>
          <span class="ml-2 text-gray-900">{{ currentData.dimensions.width }} × {{ currentData.dimensions.height }} 像素</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">掃描範圍:</span>
          <span class="ml-2 text-gray-900">{{ formatNumber(currentData.dimensions.xRange) }} × {{ formatNumber(currentData.dimensions.yRange) }} {{ currentData.physUnit }}</span>
        </div>
      </div>
    </section>

    <!-- 分析工具區域 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">分析工具</h2>
      <div class="space-y-3">
        <!-- 高度剖面量測按鈕 -->
        <button 
          @click="toggleHeightProfileMode"
          :class="[
            'w-full py-3 px-4 font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
            isProfileMode 
              ? 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400'
          ]"
        >
          <div class="flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {{ isProfileMode ? '退出高度剖面模式' : '啟動高度剖面模式' }}
          </div>
        </button>
        
        <!-- 高度剖面模式提示 -->
        <div v-if="isProfileMode" class="text-sm text-green-600 bg-green-50 p-3 rounded-lg border border-green-200">
          <div class="flex items-start">
            <svg class="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="font-medium mb-1">高度剖面量測模式已啟動</p>
              <ul class="text-xs space-y-1">
                <li>• 在圖像上左鍵點擊選擇起點</li>
                <li>• 移動滑鼠預覽剖面線</li>
                <li>• 再次左鍵點擊選擇終點</li>
                <li>• 左鍵點擊其他位置重新開始</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 影像處理區域 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">影像處理</h2>
      <div class="space-y-4">
        <!-- 平面化控制 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">平面化方法</label>
          <div class="space-y-2">
            <button 
              @click="applyFlatten('linewise_mean')"
              :disabled="imageProcessing"
              class="w-full py-2 px-3 bg-blue-100 hover:bg-blue-200 disabled:bg-gray-100 disabled:text-gray-400 text-blue-800 text-sm font-medium rounded-md transition-colors"
            >
              線性平面化 (均值)
            </button>
            <button 
              @click="applyFlatten('linewise_poly')"
              :disabled="imageProcessing"
              class="w-full py-2 px-3 bg-blue-100 hover:bg-blue-200 disabled:bg-gray-100 disabled:text-gray-400 text-blue-800 text-sm font-medium rounded-md transition-colors"
            >
              線性平面化 (多項式)
            </button>
            <button 
              @click="applyFlatten('plane')"
              :disabled="imageProcessing"
              class="w-full py-2 px-3 bg-blue-100 hover:bg-blue-200 disabled:bg-gray-100 disabled:text-gray-400 text-blue-800 text-sm font-medium rounded-md transition-colors"
            >
              全域平面擬合
            </button>
          </div>
        </div>

        <!-- 傾斜調整控制 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">傾斜調整</label>
          <div class="grid grid-cols-2 gap-2">
            <button 
              @click="adjustTilt('up')"
              :disabled="imageProcessing"
              class="py-2 px-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 text-purple-800 text-sm font-medium rounded-md transition-colors flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
              上
            </button>
            <button 
              @click="adjustTilt('down')"
              :disabled="imageProcessing"
              class="py-2 px-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 text-purple-800 text-sm font-medium rounded-md transition-colors flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              下
            </button>
            <button 
              @click="adjustTilt('left')"
              :disabled="imageProcessing"
              class="py-2 px-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 text-purple-800 text-sm font-medium rounded-md transition-colors flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              左
            </button>
            <button 
              @click="adjustTilt('right')"
              :disabled="imageProcessing"
              class="py-2 px-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:text-gray-400 text-purple-800 text-sm font-medium rounded-md transition-colors flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              右
            </button>
          </div>
          
          <!-- 微調模式切換 -->
          <div class="mt-2">
            <label class="flex items-center">
              <input 
                type="checkbox" 
                v-model="fineTuneMode" 
                class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              >
              <span class="ml-2 text-sm text-gray-700">微調模式</span>
            </label>
          </div>
        </div>

        <!-- 重置按鈕 -->
        <div>
          <button 
            @click="resetImageProcessing"
            :disabled="imageProcessing"
            class="w-full py-2 px-3 bg-red-100 hover:bg-red-200 disabled:bg-gray-100 disabled:text-gray-400 text-red-800 text-sm font-medium rounded-md transition-colors flex items-center justify-center"
          >
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            重置為原始影像
          </button>
        </div>

        <!-- 處理狀態指示 -->
        <div v-if="imageProcessing" class="text-sm text-blue-600 flex items-center bg-blue-50 p-3 rounded-lg">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          正在處理影像...
        </div>
      </div>
    </section>

    <!-- 色彩映射選擇 - 增強版本 -->
    <section v-if="currentData" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">色彩映射</h2>
      <div class="space-y-4">
        <!-- 當前選擇顯示 -->
        <div class="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
          <div class="flex items-center justify-between">
            <span>當前: <span class="font-medium text-blue-700">{{ getCurrentColormapDisplay() }}</span></span>
            <span v-if="isReversed" class="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">反轉</span>
          </div>
        </div>
        
        <!-- 色彩映射選擇器 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">選擇色彩映射</label>
          <select 
            v-model="selectedColormap"
            @change="updateColormapFromSelection"
            :disabled="isLoading || colormapUpdating"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 disabled:bg-gray-100"
          >
            <!-- 單色系 -->
            <optgroup label="單色系">
              <option value="Oranges">橘色 (Oranges)</option>
              <option value="Blues">藍色 (Blues)</option>
              <option value="Reds">紅色 (Reds)</option>
              <option value="Greens">綠色 (Greens)</option>
              <option value="Purples">紫色 (Purples)</option>
              <option value="Greys">灰階 (Greys)</option>
            </optgroup>
            
            <!-- 科學可視化 -->
            <optgroup label="科學可視化">
              <option value="Viridis">Viridis</option>
              <option value="Plasma">Plasma</option>
              <option value="Inferno">Inferno</option>
              <option value="Magma">Magma</option>
              <option value="Cividis">Cividis</option>
            </optgroup>
            
            <!-- 分歧色彩映射 -->
            <optgroup label="分歧色彩映射">
              <option value="RdYlBu">紅-黃-藍 (RdYlBu)</option>
              <option value="RdYlGn">紅-黃-綠 (RdYlGn)</option>
              <option value="Spectral">光譜 (Spectral)</option>
              <option value="Coolwarm">冷-暖 (Coolwarm)</option>
            </optgroup>
            
            <!-- 彩虹和經典 -->
            <optgroup label="彩虹和經典">
              <option value="Rainbow">彩虹 (Rainbow)</option>
              <option value="Jet">Jet</option>
              <option value="Hot">熱色 (Hot)</option>
              <option value="Cool">冷色 (Cool)</option>
            </optgroup>
            
            <!-- 地形和其他 -->
            <optgroup label="地形和其他">
              <option value="Terrain">地形 (Terrain)</option>
              <option value="Ocean">海洋 (Ocean)</option>
              <option value="Copper">銅色 (Copper)</option>
            </optgroup>
          </select>
        </div>
        
        <!-- 反轉選擇框 -->
        <div>
          <label class="flex items-center space-x-3 cursor-pointer">
            <input 
              type="checkbox" 
              v-model="isReversed"
              @change="updateColormapFromSelection"
              :disabled="isLoading || colormapUpdating"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
            >
            <span class="text-sm font-medium text-gray-700">反轉色彩映射</span>
          </label>
          <p class="text-xs text-gray-500 mt-1 ml-7">勾選後會反轉顏色順序</p>
        </div>
        
        <!-- 更新狀態指示 -->
        <div v-if="colormapUpdating" class="text-sm text-blue-600 flex items-center bg-blue-50 p-3 rounded-lg">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          正在更新色彩映射...
        </div>
      </div>
    </section>

    <!-- 統計資訊 -->
    <section v-if="currentData && currentData.statistics" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">統計資訊</h2>
      <div class="bg-gray-50 rounded-lg p-4 space-y-3 border">
        <div class="text-sm">
          <span class="font-medium text-gray-600">最小值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.min) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">最大值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.max) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">平均值:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.mean) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">RMS:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.rms) }} {{ currentData.physUnit }}</span>
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-600">範圍:</span>
          <span class="ml-2 text-gray-900 font-mono">{{ formatNumber(currentData.statistics.max - currentData.statistics.min) }} {{ currentData.physUnit }}</span>
        </div>
      </div>
    </section>

    <!-- 提示信息 -->
    <section v-if="!currentData && !isLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center text-gray-500 py-8">
        <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-lg font-medium mb-2">歡迎使用 SPM 分析器</p>
        <p class="text-sm">請選擇 TXT 檔案開始分析</p>
      </div>
    </section>

    <!-- 文件選擇區 -->
    <section v-if="isFileSelectionMode && txtFileInfo" class="flex-shrink-0">
      <h2 class="text-lg font-semibold mb-3 text-gray-800">選擇要分析的文件</h2>
      <div class="bg-gray-50 rounded-lg p-4 space-y-3 border">
        <div class="text-sm text-gray-600 mb-3">
          找到 {{ txtFileInfo.available_files.length }} 個可用文件，請選擇要分析的文件：
        </div>
        
        <!-- INT 文件 -->
        <div v-if="intFiles.length > 0" class="space-y-2">
          <h4 class="text-sm font-medium text-gray-700 flex items-center">
            <svg class="h-4 w-4 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
            </svg>
            影像文件 ({{ intFiles.length }})
          </h4>
          <div class="grid gap-2">
            <button 
              v-for="file in intFiles" 
              :key="file.filename"
              @click="selectFile(file)"
              :class="[
                'text-left p-3 rounded-md border transition-colors text-sm',
                selectedFileInfo?.filename === file.filename 
                  ? 'bg-blue-50 border-blue-300 text-blue-800' 
                  : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-700'
              ]"
            >
              <div class="font-medium">{{ file.caption }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ file.filename }}</div>
            </button>
          </div>
        </div>

        <!-- DAT 文件 -->
        <div v-if="datFiles.length > 0" class="space-y-2">
          <h4 class="text-sm font-medium text-gray-700 flex items-center">
            <svg class="h-4 w-4 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd" />
            </svg>
            電性量測文件 ({{ datFiles.length }})
          </h4>
          <div class="grid gap-2">
            <button 
              v-for="file in datFiles" 
              :key="file.filename"
              @click="selectFile(file)"
              :class="[
                'text-left p-3 rounded-md border transition-colors text-sm',
                selectedFileInfo?.filename === file.filename 
                  ? 'bg-green-50 border-green-300 text-green-800' 
                  : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-700'
              ]"
            >
              <div class="font-medium">{{ file.caption }}</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ file.filename }}
                <span v-if="file.measurement_mode" class="ml-2 px-1.5 py-0.5 bg-gray-100 rounded text-xs">
                  {{ file.measurement_mode }}
                </span>
              </div>
            </button>
          </div>
        </div>

        <!-- 操作按鈕 -->
        <div class="flex space-x-2 pt-3 border-t">
          <button 
            @click="loadSelectedFile"
            :disabled="!selectedFileInfo || isLoading"
            class="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
          >
            載入選中文件
          </button>
          <button 
            @click="cancelFileSelection"
            :disabled="isLoading"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            取消
          </button>
        </div>
      </div>
    </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import mvpStore from '../../stores/mvpStore'
import type { FileInfo } from '../../stores/mvpStore'
import { loadSPMFile, loadTxtFile, loadSelectedFile as loadSelectedFileAPI } from '../../services/apiService'

// 從 store 獲取狀態
const currentData = computed(() => mvpStore.currentData)
const isLoading = computed(() => mvpStore.isLoading)
const isProfileMode = computed(() => mvpStore.isProfileMode)

// 文件選擇相關狀態
const isFileSelectionMode = computed(() => mvpStore.isFileSelectionMode)
const txtFileInfo = computed(() => mvpStore.txtFileInfo)
const selectedFileInfo = computed(() => mvpStore.selectedFileInfo)

// 計算屬性：分類文件
const intFiles = computed(() => {
  if (!txtFileInfo.value) return []
  return txtFileInfo.value.available_files.filter(file => file.type === 'int')
})

const datFiles = computed(() => {
  if (!txtFileInfo.value) return []
  return txtFileInfo.value.available_files.filter(file => file.type === 'dat')
})

// 色彩映射控制狀態
const colormapUpdating = ref(false)
const selectedColormap = ref('Oranges')
const isReversed = ref(false)

// 影像處理控制狀態
const imageProcessing = ref(false)
const fineTuneMode = ref(false)

// 監聽當前數據變化，同步 UI 狀態
watch(currentData, (newData) => {
  if (newData) {
    // 解析當前的 colormap
    const currentColormap = newData.colormap
    if (currentColormap.endsWith('_r')) {
      selectedColormap.value = currentColormap.slice(0, -2)
      isReversed.value = true
    } else {
      selectedColormap.value = currentColormap
      isReversed.value = false
    }
  }
})

// 載入檔案 - 修改為文件選擇模式
async function handleLoadFile() {
  try {
    mvpStore.setLoading(true)
    mvpStore.setError(null)
    
    console.log('MVP: 開始選擇檔案')
    
    // 使用 pywebview 選擇檔案
    const result = await window.pywebview.api.select_txt_file()
    
    if (result.success && result.filePath) {
      console.log('MVP: 檔案選擇成功，開始解析:', result.filePath)
      
      // 載入 TXT 檔案並取得可用檔案清單
      const txtInfo = await loadTxtFile(result.filePath)
      mvpStore.setTxtFileInfo(txtInfo)
      
      console.log('MVP: TXT 檔案解析成功，找到', txtInfo.available_files.length, '個可用檔案')
    } else {
      throw new Error(result.error || '檔案選擇失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '載入檔案時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 載入檔案失敗:', err)
  } finally {
    mvpStore.setLoading(false)
  }
}

// 從選擇器更新色彩映射
async function updateColormapFromSelection() {
  if (!currentData.value) return
  
  // 構建新的 colormap 名稱
  const newColormap = isReversed.value ? `${selectedColormap.value}_r` : selectedColormap.value
  
  if (newColormap === currentData.value.colormap) {
    return // 沒有變化
  }
  
  // 確保有 intFile 才能更新色彩映射
  if (!currentData.value.intFile) {
    console.warn('MVP: 無 INT 檔案，無法更新色彩映射')
    return
  }
  
  try {
    colormapUpdating.value = true
    console.log('MVP: 開始更新色彩映射為:', newColormap)
    
    // 調用後端 API 更新色彩映射
    const result = await window.pywebview.api.update_colormap(
      currentData.value.txtFile,
      currentData.value.intFile,
      newColormap
    )
    
    if (result.success) {
      // 更新 store 中的色彩映射和 plotly 配置
      mvpStore.updateColormap(newColormap)
      if (currentData.value) {
        currentData.value.plotlyConfig = result.plotlyConfig
      }
      
      console.log('MVP: 色彩映射更新成功:', newColormap)
    } else {
      throw new Error(result.error || '更新色彩映射失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '更新色彩映射時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 更新色彩映射失敗:', err)
    
    // 恢復到之前的狀態
    if (currentData.value) {
      const currentColormap = currentData.value.colormap
      if (currentColormap.endsWith('_r')) {
        selectedColormap.value = currentColormap.slice(0, -2)
        isReversed.value = true
      } else {
        selectedColormap.value = currentColormap
        isReversed.value = false
      }
    }
  } finally {
    colormapUpdating.value = false
  }
}

// 獲取當前色彩映射的顯示名稱
function getCurrentColormapDisplay(): string {
  if (!currentData.value) return ''
  
  const colormap = currentData.value.colormap
  
  // 色彩映射顯示名稱映射
  const displayNames: Record<string, string> = {
    'Oranges': '橘色',
    'Blues': '藍色',
    'Reds': '紅色',
    'Greens': '綠色',
    'Purples': '紫色',
    'Greys': '灰階',
    'Viridis': 'Viridis',
    'Plasma': 'Plasma',
    'Inferno': 'Inferno',
    'Magma': 'Magma',
    'Cividis': 'Cividis',
    'RdYlBu': '紅-黃-藍',
    'RdYlGn': '紅-黃-綠',
    'Spectral': '光譜',
    'Coolwarm': '冷-暖',
    'Rainbow': '彩虹',
    'Jet': 'Jet',
    'Hot': '熱色',
    'Cool': '冷色',
    'Terrain': '地形',
    'Ocean': '海洋',
    'Copper': '銅色'
  }
  
  if (colormap.endsWith('_r')) {
    const baseName = colormap.slice(0, -2)
    return `${displayNames[baseName] || baseName} (反轉)`
  }
  
  return displayNames[colormap] || colormap
}

// 格式化數字顯示
function formatNumber(value: number): string {
  if (value === undefined || value === null) return 'N/A'
  
  // 根據數值大小選擇適當的小數位數
  if (Math.abs(value) >= 100) {
    return value.toFixed(1)
  } else if (Math.abs(value) >= 1) {
    return value.toFixed(2)
  } else {
    return value.toFixed(3)
  }
}

// 切換高度剖面量測模式
function toggleHeightProfileMode() {
  mvpStore.toggleProfileMode()
}

// 應用影像平面化
async function applyFlatten(method: 'linewise_mean' | 'linewise_poly' | 'plane') {
  if (!currentData.value) return
  
  try {
    imageProcessing.value = true
    console.log('MVP: 開始應用影像平面化，方法:', method)
    
    // 調用後端 API 進行影像平面化
    const result = await window.pywebview.api.apply_flatten(method)
    
    if (result.success) {
      // 更新處理後的數據，保持原有結構但替換關鍵部分
      const updatedData = {
        ...currentData.value,
        plotlyConfig: result.plotlyConfig,
        statistics: result.statistics
      }
      mvpStore.setCurrentData(updatedData)
      console.log('MVP: 影像平面化應用成功')
    } else {
      throw new Error(result.error || '應用影像平面化失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '應用影像平面化時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 應用影像平面化失敗:', err)
  } finally {
    imageProcessing.value = false
  }
}

// 調整影像傾斜
async function adjustTilt(direction: 'up' | 'down' | 'left' | 'right') {
  if (!currentData.value) return
  
  try {
    imageProcessing.value = true
    console.log('MVP: 開始調整影像傾斜，方向:', direction)
    
    // 調用後端 API 調整影像傾斜
    const result = await window.pywebview.api.adjust_tilt(direction, fineTuneMode.value)
    
    if (result.success) {
      // 更新處理後的數據，保持原有結構但替換關鍵部分
      const updatedData = {
        ...currentData.value,
        plotlyConfig: result.plotlyConfig,
        statistics: result.statistics
      }
      mvpStore.setCurrentData(updatedData)
      console.log('MVP: 影像傾斜調整成功')
    } else {
      throw new Error(result.error || '調整影像傾斜失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '調整影像傾斜時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 調整影像傾斜失敗:', err)
  } finally {
    imageProcessing.value = false
  }
}

// 重置影像處理
async function resetImageProcessing() {
  if (!currentData.value) return
  
  try {
    imageProcessing.value = true
    console.log('MVP: 開始重置影像處理')
    
    // 調用後端 API 重置影像處理
    const result = await window.pywebview.api.reset_image_processing()
    
    if (result.success) {
      // 更新為原始影像數據，保持原有結構但替換關鍵部分
      const updatedData = {
        ...currentData.value,
        plotlyConfig: result.plotlyConfig,
        statistics: result.statistics
      }
      mvpStore.setCurrentData(updatedData)
      console.log('MVP: 影像處理重置成功')
    } else {
      throw new Error(result.error || '重置影像處理失敗')
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '重置影像處理時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 重置影像處理失敗:', err)
  } finally {
    imageProcessing.value = false
  }
}

// 選擇文件
function selectFile(file: FileInfo) {
  mvpStore.setSelectedFileInfo(file)
}

// 載入選中文件
async function loadSelectedFile() {
  const selected = selectedFileInfo.value
  const txtInfo = txtFileInfo.value
  
  if (!selected || !txtInfo) return
  
  try {
    mvpStore.setLoading(true)
    mvpStore.setError(null)
    
    console.log('MVP: 開始載入選中文件:', selected.filename)
    
    // 使用新的 API 載入選中檔案
    const data = await loadSelectedFileAPI(txtInfo.txt_path, selected.filename)
    mvpStore.setCurrentData(data)
    mvpStore.exitFileSelectionMode()
    
    console.log('MVP: 選中文件載入成功:', data.name)
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '載入選中文件時發生錯誤'
    mvpStore.setError(errorMessage)
    console.error('MVP: 載入選中文件失敗:', err)
  } finally {
    mvpStore.setLoading(false)
  }
}

// 取消文件選擇
function cancelFileSelection() {
  mvpStore.exitFileSelectionMode()
}
</script>