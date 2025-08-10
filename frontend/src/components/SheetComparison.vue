<template>
  <div v-if="sheetInfo.has_multiple_sheets" class="sheet-comparison">
    <div class="card">
      <h2 class="text-2xl font-bold mb-4">Sheet Comparison</h2>
      
      <!-- Sheet Selection -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label class="block text-sm font-medium mb-2">First Sheet</label>
          <select 
            v-model="selectedSheet1" 
            @change="onSheetSelectionChange"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a sheet</option>
            <option v-for="sheet in sheetNames" :key="sheet" :value="sheet">
              {{ sheet }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-2">Second Sheet</label>
          <select 
            v-model="selectedSheet2"
            @change="onSheetSelectionChange"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a sheet</option>
            <option v-for="sheet in sheetNames" :key="sheet" :value="sheet">
              {{ sheet }}
            </option>
          </select>
        </div>
      </div>
      
      <!-- Column Selection -->
      <div v-if="selectedSheet1 && selectedSheet2 && columnsInfo.common_columns" class="mb-6">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Key Columns (for matching rows)</label>
          <div class="border rounded-lg p-3 max-h-40 overflow-y-auto">
            <div v-for="col in columnsInfo.common_columns" :key="col" class="flex items-center mb-2">
              <input 
                type="checkbox" 
                :id="`key-${col}`"
                :value="col"
                v-model="selectedKeyColumns"
                class="mr-2"
              >
              <label :for="`key-${col}`" class="text-sm">{{ col }}</label>
            </div>
          </div>
          <p class="text-xs text-gray-600 mt-1">Select columns to match rows between sheets</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-2">Comparison Columns (optional)</label>
          <div class="border rounded-lg p-3 max-h-40 overflow-y-auto">
            <div v-for="col in columnsInfo.common_columns" :key="col" class="flex items-center mb-2">
              <input 
                type="checkbox" 
                :id="`comp-${col}`"
                :value="col"
                v-model="selectedComparisonColumns"
                class="mr-2"
              >
              <label :for="`comp-${col}`" class="text-sm">{{ col }}</label>
            </div>
          </div>
          <p class="text-xs text-gray-600 mt-1">Leave empty to compare all common columns</p>
        </div>
      </div>
      
      <!-- Compare Button -->
      <div v-if="selectedSheet1 && selectedSheet2" class="mb-6">
        <button 
          @click="compareSheets"
          :disabled="selectedKeyColumns.length === 0 || loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Comparing...</span>
          <span v-else>Compare Sheets</span>
        </button>
      </div>
      
      <!-- Comparison Results -->
      <div v-if="comparisonResult" class="comparison-results">
        <h3 class="text-xl font-semibold mb-4">Comparison Results</h3>
        
        <!-- Summary -->
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">{{ comparisonResult.summary.sheet1_name }}</div>
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{ comparisonResult.summary.sheet1_rows }} rows
            </div>
          </div>
          
          <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">{{ comparisonResult.summary.sheet2_name }}</div>
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{ comparisonResult.summary.sheet2_rows }} rows
            </div>
          </div>
          
          <div class="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">Matching Rows</div>
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">
              {{ comparisonResult.summary.matching_rows }}
            </div>
          </div>
          
          <div class="bg-orange-50 dark:bg-orange-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">Only in {{ comparisonResult.summary.sheet1_name }}</div>
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {{ comparisonResult.summary.only_in_sheet1 }}
            </div>
          </div>
          
          <div class="bg-orange-50 dark:bg-orange-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">Only in {{ comparisonResult.summary.sheet2_name }}</div>
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {{ comparisonResult.summary.only_in_sheet2 }}
            </div>
          </div>
          
          <div class="bg-red-50 dark:bg-red-900 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-300">Differences Found</div>
            <div class="text-2xl font-bold text-red-600 dark:text-red-400">
              {{ comparisonResult.differences.length }}
            </div>
          </div>
        </div>
        
        <!-- Tabs for detailed results -->
        <div class="tabs">
          <div class="tab-buttons flex space-x-2 mb-4">
            <button 
              v-for="tab in resultTabs" 
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="['px-4 py-2 rounded-lg', activeTab === tab.id ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700']"
            >
              {{ tab.label }}
              <span class="ml-1 text-xs">({{ tab.count }})</span>
            </button>
          </div>
          
          <!-- Tab Content -->
          <div class="tab-content">
            <!-- Matching Rows -->
            <div v-if="activeTab === 'matching'" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th v-for="col in getTableColumns(comparisonResult.matching_rows)" :key="col" 
                        class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(row, idx) in comparisonResult.matching_rows.slice(0, 50)" :key="idx">
                    <td v-for="col in getTableColumns(comparisonResult.matching_rows)" :key="col" 
                        class="px-4 py-2 text-sm">
                      {{ formatCellValue(row[col]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="comparisonResult.matching_rows.length > 50" class="text-sm text-gray-500 mt-2">
                Showing first 50 of {{ comparisonResult.summary.matching_rows }} matching rows
              </div>
            </div>
            
            <!-- Only in Sheet 1 -->
            <div v-if="activeTab === 'only1'" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th v-for="col in getTableColumns(comparisonResult.only_in_sheet1)" :key="col" 
                        class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(row, idx) in comparisonResult.only_in_sheet1.slice(0, 50)" :key="idx">
                    <td v-for="col in getTableColumns(comparisonResult.only_in_sheet1)" :key="col" 
                        class="px-4 py-2 text-sm">
                      {{ formatCellValue(row[col]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="comparisonResult.only_in_sheet1.length > 50" class="text-sm text-gray-500 mt-2">
                Showing first 50 of {{ comparisonResult.summary.only_in_sheet1 }} rows
              </div>
            </div>
            
            <!-- Only in Sheet 2 -->
            <div v-if="activeTab === 'only2'" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th v-for="col in getTableColumns(comparisonResult.only_in_sheet2)" :key="col" 
                        class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(row, idx) in comparisonResult.only_in_sheet2.slice(0, 50)" :key="idx">
                    <td v-for="col in getTableColumns(comparisonResult.only_in_sheet2)" :key="col" 
                        class="px-4 py-2 text-sm">
                      {{ formatCellValue(row[col]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="comparisonResult.only_in_sheet2.length > 50" class="text-sm text-gray-500 mt-2">
                Showing first 50 of {{ comparisonResult.summary.only_in_sheet2 }} rows
              </div>
            </div>
            
            <!-- Differences -->
            <div v-if="activeTab === 'differences'" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key Columns</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Column</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ comparisonResult.summary.sheet1_name }} Value
                    </th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ comparisonResult.summary.sheet2_name }} Value
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(diff, idx) in comparisonResult.differences.slice(0, 100)" :key="idx">
                    <td class="px-4 py-2 text-sm">
                      <span v-for="keyCol in comparisonResult.summary.key_columns" :key="keyCol">
                        {{ keyCol }}: {{ diff[keyCol] }}<br>
                      </span>
                    </td>
                    <td class="px-4 py-2 text-sm">{{ diff.column }}</td>
                    <td class="px-4 py-2 text-sm">
                      <span class="bg-red-100 dark:bg-red-900 px-1 rounded">
                        {{ formatCellValue(diff.sheet1_value) }}
                      </span>
                    </td>
                    <td class="px-4 py-2 text-sm">
                      <span class="bg-green-100 dark:bg-green-900 px-1 rounded">
                        {{ formatCellValue(diff.sheet2_value) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="comparisonResult.differences.length > 100" class="text-sm text-gray-500 mt-2">
                Showing first 100 differences
              </div>
            </div>
          </div>
        </div>
        
        <!-- Export Options -->
        <div class="mt-6 flex space-x-2">
          <button 
            @click="exportComparison('matching')"
            class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Export Matching Rows
          </button>
          <button 
            @click="exportComparison('only1')"
            class="px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700"
          >
            Export Only in {{ comparisonResult.summary.sheet1_name }}
          </button>
          <button 
            @click="exportComparison('only2')"
            class="px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700"
          >
            Export Only in {{ comparisonResult.summary.sheet2_name }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    sessionId: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      sheetInfo: {},
      sheetNames: [],
      selectedSheet1: '',
      selectedSheet2: '',
      columnsInfo: {},
      selectedKeyColumns: [],
      selectedComparisonColumns: [],
      comparisonResult: null,
      loading: false,
      activeTab: 'matching'
    }
  },
  
  computed: {
    resultTabs() {
      if (!this.comparisonResult) return []
      return [
        { 
          id: 'matching', 
          label: 'Matching Rows', 
          count: this.comparisonResult.summary.matching_rows 
        },
        { 
          id: 'only1', 
          label: `Only in ${this.comparisonResult.summary.sheet1_name}`, 
          count: this.comparisonResult.summary.only_in_sheet1 
        },
        { 
          id: 'only2', 
          label: `Only in ${this.comparisonResult.summary.sheet2_name}`, 
          count: this.comparisonResult.summary.only_in_sheet2 
        },
        { 
          id: 'differences', 
          label: 'Differences', 
          count: this.comparisonResult.differences.length 
        }
      ]
    }
  },
  
  mounted() {
    this.loadSheetInfo()
  },
  
  methods: {
    async loadSheetInfo() {
      try {
        const response = await fetch(`/api/sheets/${this.sessionId}/`)
        const data = await response.json()
        this.sheetInfo = data
        
        if (data.has_multiple_sheets) {
          this.sheetNames = Object.keys(data.sheets)
        }
      } catch (error) {
        console.error('Error loading sheet info:', error)
      }
    },
    
    async onSheetSelectionChange() {
      if (this.selectedSheet1 && this.selectedSheet2) {
        await this.loadCommonColumns()
      }
    },
    
    async loadCommonColumns() {
      try {
        const response = await fetch(
          `/api/sheets/${this.sessionId}/columns/?sheet1=${this.selectedSheet1}&sheet2=${this.selectedSheet2}`
        )
        this.columnsInfo = await response.json()
        
        // Reset selections
        this.selectedKeyColumns = []
        this.selectedComparisonColumns = []
        this.comparisonResult = null
      } catch (error) {
        console.error('Error loading columns:', error)
      }
    },
    
    async compareSheets() {
      if (this.selectedKeyColumns.length === 0) {
        alert('Please select at least one key column for matching')
        return
      }
      
      this.loading = true
      try {
        const response = await fetch(`/api/sheets/${this.sessionId}/compare/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            sheet1: this.selectedSheet1,
            sheet2: this.selectedSheet2,
            key_columns: this.selectedKeyColumns,
            comparison_columns: this.selectedComparisonColumns.length > 0 
              ? this.selectedComparisonColumns 
              : null
          })
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Comparison failed')
        }
        
        this.comparisonResult = await response.json()
        this.activeTab = 'matching'
      } catch (error) {
        console.error('Error comparing sheets:', error)
        alert('Error comparing sheets: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    getTableColumns(rows) {
      if (!rows || rows.length === 0) return []
      // Get columns from first row, excluding columns ending with _sheet1 or _sheet2
      return Object.keys(rows[0]).filter(col => !col.endsWith('_sheet1') && !col.endsWith('_sheet2'))
    },
    
    formatCellValue(value) {
      if (value === null || value === undefined) return ''
      if (typeof value === 'object') return JSON.stringify(value)
      return String(value)
    },
    
    exportComparison(type) {
      let data = []
      let filename = ''
      
      switch(type) {
        case 'matching':
          data = this.comparisonResult.matching_rows
          filename = `matching_rows_${this.selectedSheet1}_${this.selectedSheet2}.csv`
          break
        case 'only1':
          data = this.comparisonResult.only_in_sheet1
          filename = `only_in_${this.selectedSheet1}.csv`
          break
        case 'only2':
          data = this.comparisonResult.only_in_sheet2
          filename = `only_in_${this.selectedSheet2}.csv`
          break
      }
      
      if (data.length === 0) {
        alert('No data to export')
        return
      }
      
      // Convert to CSV
      const headers = Object.keys(data[0])
      const csvContent = [
        headers.join(','),
        ...data.map(row => 
          headers.map(header => {
            const value = row[header]
            if (value === null || value === undefined) return ''
            const str = String(value)
            // Escape quotes and wrap in quotes if contains comma or quotes
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
              return `"${str.replace(/"/g, '""')}"`
            }
            return str
          }).join(',')
        )
      ].join('\n')
      
      // Download
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
.sheet-comparison {
  padding: 1rem;
}

.card {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark .card {
  background: #1f2937;
}

table {
  font-size: 0.875rem;
}

td {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
