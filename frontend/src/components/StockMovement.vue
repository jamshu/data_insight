<template>
  <div class="space-y-6">
    <!-- Validation Section -->
    <div v-if="!isValidated" class="card p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Stock Movement File Validation
      </h3>
      <div class="mb-4">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
          First, let's validate that your uploaded file is a proper stock movement report.
        </p>
        <button @click="validateFile" 
                :disabled="validating"
                class="btn-primary flex items-center space-x-2">
          <svg v-if="validating" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ validating ? 'Validating...' : 'Validate Stock Movement File' }}</span>
        </button>
      </div>
      
      <!-- Validation Result -->
      <div v-if="validationResult" class="mt-4">
        <div v-if="validationResult.is_valid_stock_movement" 
             class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <div>
              <h4 class="font-medium text-green-800 dark:text-green-200">Valid Stock Movement File</h4>
              <p class="text-sm text-green-600 dark:text-green-400 mt-1">{{ validationResult.message }}</p>
              <p class="text-sm text-green-600 dark:text-green-400 mt-1">
                Columns: {{ validationResult.shape[1] }}, Rows: {{ validationResult.shape[0] }}
              </p>
            </div>
          </div>
        </div>
        <div v-else 
             class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <div>
              <h4 class="font-medium text-red-800 dark:text-red-200">Invalid Stock Movement File</h4>
              <p class="text-sm text-red-600 dark:text-red-400 mt-1">{{ validationResult.message }}</p>
              <div v-if="validationResult.missing_columns" class="mt-2">
                <p class="text-sm text-red-600 dark:text-red-400">Missing columns:</p>
                <ul class="list-disc list-inside text-xs text-red-500 dark:text-red-400 mt-1">
                  <li v-for="col in validationResult.missing_columns" :key="col">{{ col }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Configuration Section -->
    <div v-if="isValidated" class="card p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Stock Movement Configuration
      </h3>
      
      <!-- Column Selection -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <!-- UOM Column -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            UOM Column
          </label>
          <select v-model="config.uom_column" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">Select UOM Column</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        
        <!-- From Location Column -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            From Location Column
          </label>
          <select v-model="config.location_from_column" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">Select From Location Column</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        
        <!-- To Location Column -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            To Location Column
          </label>
          <select v-model="config.location_to_column" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">Select To Location Column</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        
        <!-- Quantity Column -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quantity Column
          </label>
          <select v-model="config.quantity_column" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">Select Quantity Column</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        
        <!-- Date Column (Optional) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Date Column (Optional)
          </label>
          <select v-model="config.date_column" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">No Date Sorting</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        
        <!-- Check Location -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Check Location (for Sign +)
          </label>
          <input v-model="config.check_location" 
                 type="text"
                 placeholder="e.g., JDFCW/Jeddah Factory"
                 class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
        </div>
      </div>
      
      <!-- UOM Mappings -->
      <div class="mb-6">
        <div class="flex justify-between items-center mb-3">
          <h4 class="text-md font-medium text-gray-800 dark:text-gray-200">
            UOM to Units Mapping
          </h4>
          <button @click="addUOMMapping" 
                  class="btn-secondary text-sm flex items-center space-x-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Mapping</span>
          </button>
        </div>
        
        <div class="space-y-2">
          <div v-for="(mapping, index) in config.uom_mappings" :key="index" 
               class="flex items-center space-x-2">
            <input v-model="mapping.uom_name" 
                   type="text"
                   placeholder="UOM Name (e.g., Cartons-24)"
                   class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <input v-model.number="mapping.units" 
                   type="number"
                   placeholder="Units"
                   class="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <button @click="removeUOMMapping(index)" 
                    class="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
          
          <!-- Default mappings hint -->
          <div v-if="config.uom_mappings.length === 0" 
               class="text-sm text-gray-500 dark:text-gray-400 italic">
            Add UOM mappings to convert units (e.g., Cartons-24 → 24 units)
          </div>
        </div>
      </div>
      
      <!-- Process Button -->
      <div class="flex justify-end space-x-3">
        <button @click="loadSampleConfig" 
                class="btn-secondary">
          Load Sample Config
        </button>
        <button @click="processStockMovement" 
                :disabled="!isConfigValid || processing"
                class="btn-primary flex items-center space-x-2">
          <svg v-if="processing" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ processing ? 'Processing...' : 'Process Stock Movement' }}</span>
        </button>
      </div>
    </div>
    
    <!-- Results Section -->
    <div v-if="results" class="space-y-6">
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="card p-4">
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Rows</h3>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatNumber(results.summary.total_rows) }}
          </p>
        </div>
        <div class="card p-4">
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Inbound</h3>
          <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
            +{{ formatNumber(results.summary.total_inbound) }}
          </p>
        </div>
        <div class="card p-4">
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Outbound</h3>
          <p class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">
            {{ formatNumber(results.summary.total_outbound) }}
          </p>
        </div>
        <div class="card p-4">
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Final Balance</h3>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ formatNumber(results.summary.final_balance) }}
          </p>
        </div>
      </div>
      
      <!-- Data Table with Running Balance -->
      <div class="card">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Processed Stock Movement Data
          </h3>
          <div class="flex space-x-2">
            <button @click="exportData" 
                    class="btn-secondary flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Export Excel</span>
            </button>
          </div>
        </div>
        
        <div class="overflow-x-auto max-h-96">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700 sticky top-0">
              <tr>
                <th v-for="col in displayColumns" :key="col" 
                    class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(row, idx) in paginatedData" :key="idx" 
                  class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td v-for="col in displayColumns" :key="col" 
                    class="px-4 py-3 text-sm whitespace-nowrap"
                    :class="getCellClass(col, row[col])">
                  {{ formatCellValue(col, row[col]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, results.processed_data.length) }} of {{ results.processed_data.length }} entries
          </div>
          <div class="flex space-x-2">
            <button @click="currentPage--" 
                    :disabled="currentPage === 1"
                    class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50">
              Previous
            </button>
            <span class="px-3 py-1">Page {{ currentPage }} of {{ totalPages }}</span>
            <button @click="currentPage++" 
                    :disabled="currentPage === totalPages"
                    class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50">
              Next
            </button>
          </div>
        </div>
      </div>
      
      <!-- Chart Visualization -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Running Balance Trend
        </h3>
        <div id="stock-balance-chart" class="h-64"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import Plotly from 'plotly.js-dist'
import { useNotification } from '../utils/notification'

const props = defineProps({
  sessionId: {
    type: String,
    required: true
  }
})

const { showNotification } = useNotification()

// State
const availableColumns = ref([])
const processing = ref(false)
const results = ref(null)
const currentPage = ref(1)
const pageSize = ref(50)
const validating = ref(false)
const validationResult = ref(null)
const isValidated = ref(false)

// Configuration
const config = ref({
  uom_column: '',
  location_from_column: '',
  location_to_column: '',
  quantity_column: '',
  date_column: '',
  check_location: 'JDFCW/Jeddah Factory',
  uom_mappings: []
})

// Computed
const isConfigValid = computed(() => {
  return config.value.uom_column && 
         config.value.location_from_column && 
         config.value.location_to_column && 
         config.value.quantity_column && 
         config.value.check_location
})

const displayColumns = computed(() => {
  if (!results.value || !results.value.columns) return []
  
  // Prioritize new calculated columns
  const priorityColumns = ['UOM_Qty_Done', 'Sign', 'UOM_Done_Qty', 'Running_Balance']
  const otherColumns = results.value.columns.filter(col => !priorityColumns.includes(col))
  
  return [...otherColumns, ...priorityColumns.filter(col => results.value.columns.includes(col))]
})

const paginatedData = computed(() => {
  if (!results.value || !results.value.processed_data) return []
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  
  return results.value.processed_data.slice(start, end)
})

const totalPages = computed(() => {
  if (!results.value || !results.value.processed_data) return 1
  return Math.ceil(results.value.processed_data.length / pageSize.value)
})

// Methods
const validateFile = async () => {
  validating.value = true
  try {
    const response = await axios.get(`/api/stock-movement/validate/${props.sessionId}`)
    validationResult.value = response.data
    
    if (response.data.is_valid_stock_movement) {
      isValidated.value = true
      availableColumns.value = response.data.columns
      
      // Auto-populate fields based on standard column names
      if (response.data.columns.includes('Unit of Measure')) {
        config.value.uom_column = 'Unit of Measure'
      }
      if (response.data.columns.includes('From')) {
        config.value.location_from_column = 'From'
      }
      if (response.data.columns.includes('To')) {
        config.value.location_to_column = 'To'
      }
      if (response.data.columns.includes('Done')) {
        config.value.quantity_column = 'Done'
      }
      if (response.data.columns.includes('Date')) {
        config.value.date_column = 'Date'
      }
      
      showNotification('File validation successful!', 'success')
    } else {
      showNotification('File is not a valid stock movement report', 'warning')
    }
  } catch (error) {
    console.error('Failed to validate file:', error)
    showNotification('Failed to validate file', 'error')
  } finally {
    validating.value = false
  }
}

const fetchColumns = async () => {
  try {
    const response = await axios.get(`/api/stock-movement/columns/${props.sessionId}`)
    availableColumns.value = response.data.columns
  } catch (error) {
    console.error('Failed to fetch columns:', error)
    showNotification('Failed to load columns', 'error')
  }
}

const addUOMMapping = () => {
  config.value.uom_mappings.push({ uom_name: '', units: 1 })
}

const removeUOMMapping = (index) => {
  config.value.uom_mappings.splice(index, 1)
}

const loadSampleConfig = () => {
  config.value.uom_mappings = [
    { uom_name: 'Cartons-24', units: 24 },
    { uom_name: 'Cartons-50', units: 50 },
    { uom_name: 'Cartons-12', units: 12 },
    { uom_name: 'Units', units: 1 }
  ]
  showNotification('Sample configuration loaded', 'success')
}

const processStockMovement = async () => {
  if (!isConfigValid.value) {
    showNotification('Please fill in all required fields', 'warning')
    return
  }
  
  processing.value = true
  try {
    const response = await axios.post('/api/stock-movement/process', {
      session_id: props.sessionId,
      ...config.value
    })
    
    if (response.data.success) {
      results.value = response.data
      currentPage.value = 1
      showNotification('Stock movement processed successfully', 'success')
      
      // Create visualization
      await nextTick()
      createBalanceChart()
    } else {
      showNotification(response.data.message, 'error')
    }
  } catch (error) {
    console.error('Failed to process stock movement:', error)
    showNotification('Failed to process stock movement', 'error')
  } finally {
    processing.value = false
  }
}

const exportData = async () => {
  try {
    const response = await axios.post(`/api/stock-movement/export/${props.sessionId}`, {
      session_id: props.sessionId,
      ...config.value
    })
    
    if (response.data.success) {
      // Download the file
      window.open(`/uploads/${response.data.filename}`, '_blank')
      showNotification('Data exported successfully', 'success')
    }
  } catch (error) {
    console.error('Failed to export data:', error)
    showNotification('Failed to export data', 'error')
  }
}

const createBalanceChart = () => {
  if (!results.value || !results.value.processed_data) return
  
  const data = results.value.processed_data
  const xData = data.map((_, idx) => idx + 1)
  const yData = data.map(row => row.Running_Balance)
  
  const trace = {
    x: xData,
    y: yData,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Running Balance',
    line: {
      color: 'rgb(59, 130, 246)',
      width: 2
    },
    marker: {
      size: 4
    }
  }
  
  const layout = {
    title: 'Stock Movement Running Balance',
    xaxis: {
      title: 'Transaction Number'
    },
    yaxis: {
      title: 'Running Balance'
    },
    hovermode: 'x unified',
    margin: { t: 40, r: 20, l: 60, b: 40 }
  }
  
  Plotly.newPlot('stock-balance-chart', [trace], layout, { responsive: true })
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '0'
  return new Intl.NumberFormat().format(value)
}

const formatCellValue = (column, value) => {
  if (value === null || value === undefined) return ''
  
  if (['UOM_Qty_Done', 'Sign', 'UOM_Done_Qty', 'Running_Balance', 'Done'].includes(column)) {
    return formatNumber(value)
  }
  
  // Format dates
  if (column === 'Date' && value && typeof value === 'string' && value.includes('T')) {
    return new Date(value).toLocaleDateString()
  }
  
  return value
}

const getCellClass = (column, value) => {
  const classes = ['text-gray-900 dark:text-white']
  
  if (column === 'Sign' || column === 'UOM_Done_Qty') {
    if (value > 0) classes.push('text-green-600 dark:text-green-400')
    else if (value < 0) classes.push('text-red-600 dark:text-red-400')
  }
  
  if (column === 'Running_Balance') {
    classes.push('font-semibold')
    if (value < 0) classes.push('text-red-600 dark:text-red-400')
    else classes.push('text-green-600 dark:text-green-400')
  }
  
  if (['UOM_Qty_Done'].includes(column)) {
    classes.push('font-medium')
  }
  
  return classes.join(' ')
}

// Lifecycle
onMounted(() => {
  // Start by validating the file instead of just fetching columns
  // fetchColumns()
})

// Watch for session changes
watch(() => props.sessionId, () => {
  isValidated.value = false
  validationResult.value = null
  results.value = null
  // Reset configuration
  config.value = {
    uom_column: '',
    location_from_column: '',
    location_to_column: '',
    quantity_column: '',
    date_column: '',
    check_location: 'JDFCW/Jeddah Factory',
    uom_mappings: []
  }
})
</script>
