<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-center">
        <svg class="animate-spin h-12 w-12 text-primary-600 mx-auto" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-500 dark:text-gray-400">Loading analysis...</p>
      </div>
    </div>

    <!-- Analysis Content -->
    <div v-else-if="analysisData">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Data Analysis</h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ analysisData.filename }} • {{ formatNumber(analysisData.rows) }} rows • {{ analysisData.columns }} columns
          </p>
        </div>
        <div class="flex space-x-3">
          <button @click="exportData('csv')" class="btn-secondary flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Export</span>
          </button>
          <button @click="refreshAnalysis" class="btn-primary flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8">
          <button v-for="tab in tabs" :key="tab.id"
                  @click="activeTab = tab.id"
                  :class="[
                    'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                    activeTab === tab.id 
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  ]">
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="mt-6">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Quick Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="card p-6">
              <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Missing Values</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                {{ analysisData.patterns?.missing_percentage?.toFixed(1) || 0 }}%
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ analysisData.patterns?.total_missing || 0 }} cells
              </p>
            </div>
            <div class="card p-6">
              <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Duplicates</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                {{ analysisData.patterns?.duplicate_rows || 0 }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                duplicate rows found
              </p>
            </div>
            <div class="card p-6">
              <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">Data Quality</h3>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                {{ ((1 - (analysisData.patterns?.missing_percentage || 0) / 100) * 100).toFixed(0) }}%
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                completeness score
              </p>
            </div>
          </div>

          <!-- Column Statistics -->
          <div class="card">
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Column Statistics</h2>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Column</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Missing</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Unique</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Mean/Mode</th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="stat in analysisData.column_stats" :key="stat.column" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ stat.column }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ stat.dtype }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ stat.missing }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ stat.unique }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {{ stat.mean !== null ? stat.mean.toFixed(2) : (stat.mode || 'N/A') }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Visualizations Tab -->
        <div v-if="activeTab === 'visualizations'" class="space-y-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Distribution Chart -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Data Distribution</h3>
              <div id="distribution-chart" class="h-64"></div>
            </div>

            <!-- Correlation Heatmap -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Correlation Matrix</h3>
              <div id="correlation-chart" class="h-64"></div>
            </div>

            <!-- Missing Data Pattern -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Missing Data Pattern</h3>
              <div id="missing-chart" class="h-64"></div>
            </div>

            <!-- Time Series (if applicable) -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Trends Over Time</h3>
              <div id="timeseries-chart" class="h-64"></div>
            </div>
          </div>
        </div>

        <!-- Data Preview Tab -->
        <div v-if="activeTab === 'data'" class="card">
          <div class="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Data Preview</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th v-for="col in dataColumns" :key="col" 
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="(row, idx) in dataSample" :key="idx" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td v-for="col in dataColumns" :key="col" 
                      class="px-6 py-4 text-sm text-gray-900 dark:text-white whitespace-nowrap">
                    {{ row[col] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Group By Tab -->
        <div v-if="activeTab === 'groupby'" class="space-y-6">
          <!-- Group By Controls -->
          <div class="card p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Group By Analysis</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Group By Column
                </label>
                <select v-model="groupByConfig.column" 
                        @change="performGroupBy"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Select column...</option>
                  <option v-for="col in categoricalColumns" :key="col" :value="col">
                    {{ col }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Aggregate Column
                </label>
                <select v-model="groupByConfig.aggColumn" 
                        @change="performGroupBy"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Select column...</option>
                  <option v-for="col in numericColumns" :key="col" :value="col">
                    {{ col }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Aggregation Function
                </label>
                <select v-model="groupByConfig.aggFunc" 
                        @change="performGroupBy"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="mean">Mean</option>
                  <option value="sum">Sum</option>
                  <option value="count">Count</option>
                  <option value="max">Max</option>
                  <option value="min">Min</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Group By Results -->
          <div v-if="groupByResults" class="card">
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ groupByConfig.column }} by {{ groupByConfig.aggFunc === 'count' ? 'Count' : groupByConfig.aggColumn }}
              </h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                      {{ groupByConfig.column }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                      {{ groupByConfig.aggFunc === 'count' ? 'Count' : groupByConfig.aggColumn }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(row, idx) in groupByResults" :key="idx" 
                      class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                      @click="showFilteredData(groupByConfig.column, row[groupByConfig.column])">
                    <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {{ row[groupByConfig.column] }}
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {{ formatValue(row[groupByConfig.aggFunc === 'count' ? 'count' : groupByConfig.aggColumn]) }}
                    </td>
                    <td class="px-6 py-4 text-sm">
                      <button class="text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300">
                        View Data →
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Group By Chart -->
          <div v-if="groupByResults && groupByResults.length > 0" class="card p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Visualization</h3>
            <div id="groupby-chart" class="h-64"></div>
          </div>
        </div>

        <!-- Patterns Tab -->
        <div v-if="activeTab === 'patterns'" class="space-y-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Outliers -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Outliers Detected</h3>
              <div v-if="analysisData.patterns?.outliers">
                <div v-for="(outliers, col) in analysisData.patterns.outliers" :key="col" 
                     class="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ col }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ outliers.length }} outliers found</p>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 dark:text-gray-400">No outliers detected</p>
            </div>

            <!-- Data Quality Issues -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quality Issues</h3>
              <div class="space-y-3">
                <div v-for="issue in analysisData.patterns?.quality_issues" :key="issue.type"
                     class="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ issue.description }}</span>
                  <span class="text-xs px-2 py-1 bg-yellow-200 dark:bg-yellow-800 rounded">{{ issue.severity }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900 dark:text-white">No analysis data available</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Upload a file to start analyzing</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import Plotly from 'plotly.js-dist'
import { useNotification } from '../utils/notification'

const route = useRoute()
const { showNotification } = useNotification()

const loading = ref(false)
const analysisData = ref(null)
const activeTab = ref('overview')
const dataColumns = ref([])
const dataSample = ref([])

const tabs = [
  { id: 'overview', name: 'Overview' },
  { id: 'visualizations', name: 'Visualizations' },
  { id: 'data', name: 'Data Preview' },
  { id: 'groupby', name: 'Group By' },
  { id: 'patterns', name: 'Patterns & Insights' }
]

// Group by state
const groupByConfig = ref({
  column: '',
  aggColumn: '',
  aggFunc: 'mean'
})
const groupByResults = ref(null)
const categoricalColumns = ref([])
const numericColumns = ref([])
const filteredData = ref(null)
const showFilterModal = ref(false)

const fetchAnalysis = async (sessionId) => {
  if (!sessionId) return
  
  loading.value = true
  try {
    const response = await axios.get(`/api/analysis/${sessionId}`)
    analysisData.value = response.data
    
    // Extract data sample
    if (response.data.sample) {
      dataColumns.value = Object.keys(response.data.sample[0] || {})
      dataSample.value = response.data.sample
    }
    
    // Categorize columns for group-by
    if (response.data.column_stats) {
      categoricalColumns.value = response.data.column_stats
        .filter(stat => stat.dtype === 'object' || stat.dtype === 'string' || stat.unique < 50)
        .map(stat => stat.column)
      
      numericColumns.value = response.data.column_stats
        .filter(stat => stat.dtype.includes('int') || stat.dtype.includes('float'))
        .map(stat => stat.column)
    }
    
    // Create visualizations after data is loaded
    await nextTick()
    if (activeTab.value === 'visualizations') {
      createVisualizations()
    }
  } catch (error) {
    console.error('Failed to fetch analysis:', error)
    
    // Handle different error scenarios
    if (error.response?.status === 404) {
      showNotification('Session not found. Please upload a new file.', 'warning')
      // Optionally redirect to dashboard
      setTimeout(() => {
        window.location.href = '/'
      }, 2000)
    } else if (error.response?.status === 500) {
      showNotification('Server error. Please try again or upload a new file.', 'error')
    } else {
      showNotification('Failed to load analysis data', 'error')
    }
    
    // Clear invalid data
    analysisData.value = null
  } finally {
    loading.value = false
  }
}

const createVisualizations = async () => {
  if (!analysisData.value) return
  
  // Wait for DOM to be ready
  await nextTick()
  
  // Create distribution chart
  const distributionDiv = document.getElementById('distribution-chart')
  if (distributionDiv && analysisData.value.distributions) {
    const firstNumCol = Object.keys(analysisData.value.distributions)[0]
    if (firstNumCol) {
      const data = [{
        x: analysisData.value.distributions[firstNumCol],
        type: 'histogram',
        marker: { color: '#3b82f6' }
      }]
      const layout = {
        title: firstNumCol,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#9ca3af' }
      }
      Plotly.newPlot(distributionDiv, data, layout, { responsive: true })
    }
  }
  
  // Create correlation heatmap
  const correlationDiv = document.getElementById('correlation-chart')
  if (correlationDiv && analysisData.value.correlations) {
    const corr = analysisData.value.correlations
    const data = [{
      z: corr.values || [],
      x: corr.columns || [],
      y: corr.columns || [],
      type: 'heatmap',
      colorscale: 'RdBu'
    }]
    const layout = {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#9ca3af' }
    }
    Plotly.newPlot(correlationDiv, data, layout, { responsive: true })
  }
}

const refreshAnalysis = () => {
  const sessionId = route.params.sessionId
  if (sessionId) {
    fetchAnalysis(sessionId)
  }
}

const exportData = async (format) => {
  const sessionId = route.params.sessionId
  if (!sessionId) return
  
  try {
    const response = await axios.get(`/api/export/${sessionId}`, {
      params: { format },
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `analysis_${sessionId}.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    showNotification('Export completed successfully', 'success')
  } catch (error) {
    console.error('Export failed:', error)
    showNotification('Failed to export data', 'error')
  }
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatValue = (value) => {
  if (typeof value === 'number') {
    if (Number.isInteger(value)) {
      return formatNumber(value)
    }
    return value.toFixed(2)
  }
  return value
}

// Group by functionality
const performGroupBy = async () => {
  const sessionId = route.params.sessionId
  if (!sessionId || !groupByConfig.value.column) return
  
  // For count, we don't need an aggregation column
  if (groupByConfig.value.aggFunc !== 'count' && !groupByConfig.value.aggColumn) return
  
  try {
    const response = await axios.post(`/api/analysis/${sessionId}/custom`, {
      type: 'groupby',
      group_column: groupByConfig.value.column,
      agg_column: groupByConfig.value.aggColumn,
      agg_func: groupByConfig.value.aggFunc
    })
    
    groupByResults.value = response.data
    
    // Create group by chart
    await nextTick()
    createGroupByChart()
  } catch (error) {
    console.error('Group by failed:', error)
    showNotification('Failed to perform group by analysis', 'error')
  }
}

const createGroupByChart = () => {
  const chartDiv = document.getElementById('groupby-chart')
  if (!chartDiv || !groupByResults.value) return
  
  const xValues = groupByResults.value.map(row => row[groupByConfig.value.column])
  const yValues = groupByResults.value.map(row => {
    const key = groupByConfig.value.aggFunc === 'count' ? 'count' : groupByConfig.value.aggColumn
    return row[key]
  })
  
  const data = [{
    x: xValues,
    y: yValues,
    type: 'bar',
    marker: { color: '#3b82f6' }
  }]
  
  const layout = {
    title: `${groupByConfig.value.column} by ${groupByConfig.value.aggFunc === 'count' ? 'Count' : groupByConfig.value.aggColumn}`,
    xaxis: { title: groupByConfig.value.column },
    yaxis: { title: groupByConfig.value.aggFunc === 'count' ? 'Count' : `${groupByConfig.value.aggFunc} of ${groupByConfig.value.aggColumn}` },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#9ca3af' }
  }
  
  Plotly.newPlot(chartDiv, data, layout, { responsive: true })
}

const showFilteredData = async (column, value) => {
  const sessionId = route.params.sessionId
  if (!sessionId) return
  
  try {
    const response = await axios.post(`/api/analysis/${sessionId}/custom`, {
      type: 'filter',
      column: column,
      operator: '=',
      value: value
    })
    
    if (response.data.sample) {
      // Update data preview with filtered data
      dataSample.value = response.data.sample
      activeTab.value = 'data'
      
      showNotification(`Showing ${response.data.rows_matched} rows where ${column} = ${value}`, 'success')
    }
  } catch (error) {
    console.error('Filter failed:', error)
    showNotification('Failed to filter data', 'error')
  }
}

// Watch for tab changes to create visualizations
watch(activeTab, async (newTab) => {
  if (newTab === 'visualizations' && analysisData.value) {
    await nextTick()
    createVisualizations()
  }
})

// Watch for route changes
watch(() => route.params.sessionId, (newSessionId) => {
  if (newSessionId) {
    fetchAnalysis(newSessionId)
  }
})

onMounted(() => {
  const sessionId = route.params.sessionId
  if (sessionId) {
    fetchAnalysis(sessionId)
  }
})
</script>
