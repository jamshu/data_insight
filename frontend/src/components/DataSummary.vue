<template>
  <div class="data-summary p-6 space-y-6">
    <!-- Header Section -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">Data Summary</h2>
      <p class="text-gray-600">Quick overview and insights from your dataset</p>
    </div>

    <!-- Key Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm">Total Rows</p>
            <p class="text-3xl font-bold">{{ formatNumber(summary.totalRows) }}</p>
          </div>
          <svg class="w-12 h-12 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m-5 0h5m-5 0l1-9h3l1 9m-5 0H9m5 0h1M10 5h4"></path>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-md p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm">Total Columns</p>
            <p class="text-3xl font-bold">{{ summary.totalColumns }}</p>
          </div>
          <svg class="w-12 h-12 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-md p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm">Missing Values</p>
            <p class="text-3xl font-bold">{{ formatPercent(summary.missingPercent) }}%</p>
          </div>
          <svg class="w-12 h-12 text-purple-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow-md p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-orange-100 text-sm">Data Quality Score</p>
            <p class="text-3xl font-bold">{{ summary.qualityScore }}%</p>
          </div>
          <svg class="w-12 h-12 text-orange-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Data Types Distribution -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Data Types Distribution</h3>
        <div ref="dataTypesChart" class="h-64"></div>
      </div>

      <!-- Missing Data Heatmap -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Missing Data Overview</h3>
        <div ref="missingDataChart" class="h-64"></div>
      </div>
    </div>

    <!-- Column Statistics Table -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Column Statistics</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Column</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Non-Null</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unique</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mean/Mode</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Min/Max</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="col in columnStats" :key="col.name" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ col.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :class="getTypeClass(col.dtype)">{{ col.dtype }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatNumber(col.non_null) }} ({{ formatPercent(col.non_null_percent) }}%)
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ col.unique }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ col.mean !== null ? formatValue(col.mean) : col.mode || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ col.min !== null ? `${formatValue(col.min)} / ${formatValue(col.max)}` : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Key Insights -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Patterns & Anomalies -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Key Patterns & Anomalies</h3>
        <ul class="space-y-3">
          <li v-for="(insight, index) in insights" :key="index" class="flex items-start">
            <span :class="getInsightIcon(insight.type)" class="flex-shrink-0 mt-1"></span>
            <span class="ml-3 text-sm text-gray-700">{{ insight.message }}</span>
          </li>
        </ul>
      </div>

      <!-- Top Correlations -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Top Correlations</h3>
        <div v-if="topCorrelations.length > 0" class="space-y-2">
          <div v-for="corr in topCorrelations" :key="`${corr.col1}-${corr.col2}`" class="flex items-center justify-between">
            <span class="text-sm text-gray-700">{{ corr.col1 }} ↔ {{ corr.col2 }}</span>
            <span :class="getCorrelationClass(corr.value)" class="text-sm font-semibold">
              {{ corr.value.toFixed(3) }}
            </span>
          </div>
        </div>
        <p v-else class="text-sm text-gray-500">No significant correlations found</p>
      </div>
    </div>

    <!-- Data Sample Preview -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Data Sample</h3>
        <button @click="refreshSample" class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600">
          Refresh Sample
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="col in sampleColumns" :key="col" 
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, index) in sampleData" :key="index" class="hover:bg-gray-50">
              <td v-for="col in sampleColumns" :key="col" 
                  class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatCellValue(row[col]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Export Options -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Export Summary</h3>
      <div class="flex space-x-4">
        <button @click="exportSummary('pdf')" 
                class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
          Export as PDF
        </button>
        <button @click="exportSummary('html')" 
                class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
          Export as HTML
        </button>
        <button @click="exportSummary('json')" 
                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Export as JSON
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import Plotly from 'plotly.js-dist'

const route = useRoute()
const sessionId = route.params.id

// Refs
const dataTypesChart = ref(null)
const missingDataChart = ref(null)

// Data
const summary = ref({
  totalRows: 0,
  totalColumns: 0,
  missingPercent: 0,
  qualityScore: 0
})

const columnStats = ref([])
const insights = ref([])
const topCorrelations = ref([])
const sampleData = ref([])
const sampleColumns = ref([])

// Fetch data summary
const fetchSummary = async () => {
  try {
    // Fetch basic info
    const infoResponse = await fetch(`http://localhost:8000/api/analysis/info/?session_id=${sessionId}`)
    const info = await infoResponse.json()
    
    summary.value.totalRows = info.num_rows
    summary.value.totalColumns = info.num_columns
    
    // Fetch column stats
    const statsResponse = await fetch(`http://localhost:8000/api/analysis/column-stats/?session_id=${sessionId}`)
    const stats = await statsResponse.json()
    columnStats.value = stats.stats
    
    // Calculate missing percentage
    const totalCells = info.num_rows * info.num_columns
    const totalMissing = stats.stats.reduce((sum, col) => sum + (info.num_rows - col.non_null), 0)
    summary.value.missingPercent = (totalMissing / totalCells * 100).toFixed(1)
    
    // Calculate quality score (simple heuristic)
    const missingScore = Math.max(0, 100 - summary.value.missingPercent * 2)
    const uniquenessScore = stats.stats.reduce((sum, col) => {
      const uniqueRatio = col.unique / info.num_rows
      return sum + (uniqueRatio > 0.95 ? 50 : uniqueRatio * 100)
    }, 0) / info.num_columns
    summary.value.qualityScore = Math.round((missingScore + uniquenessScore) / 2)
    
    // Fetch correlations
    const corrResponse = await fetch(`http://localhost:8000/api/analysis/correlations/?session_id=${sessionId}`)
    const corrData = await corrResponse.json()
    if (corrData.correlations && corrData.correlations.length > 0) {
      // Extract top correlations
      const correlationPairs = []
      const columns = corrData.correlations[0]
      for (let i = 0; i < corrData.correlations.length; i++) {
        for (let j = i + 1; j < corrData.correlations[i].length; j++) {
          const value = corrData.correlations[i][j]
          if (Math.abs(value) > 0.5 && Math.abs(value) < 1) {
            correlationPairs.push({
              col1: columns[i],
              col2: columns[j],
              value: value
            })
          }
        }
      }
      topCorrelations.value = correlationPairs
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
        .slice(0, 5)
    }
    
    // Fetch data sample
    await fetchSample()
    
    // Generate insights
    generateInsights()
    
    // Create visualizations
    createDataTypesChart()
    createMissingDataChart()
    
  } catch (error) {
    console.error('Error fetching summary:', error)
  }
}

// Fetch data sample
const fetchSample = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/analysis/sample/?session_id=${sessionId}&n=5`)
    const data = await response.json()
    if (data.sample && data.sample.length > 0) {
      sampleColumns.value = Object.keys(data.sample[0])
      sampleData.value = data.sample
    }
  } catch (error) {
    console.error('Error fetching sample:', error)
  }
}

// Generate insights
const generateInsights = () => {
  const newInsights = []
  
  // Check for missing data
  if (summary.value.missingPercent > 20) {
    newInsights.push({
      type: 'warning',
      message: `High amount of missing data detected (${summary.value.missingPercent}%)`
    })
  }
  
  // Check for columns with low variance
  columnStats.value.forEach(col => {
    if (col.unique === 1) {
      newInsights.push({
        type: 'info',
        message: `Column "${col.name}" has only one unique value`
      })
    } else if (col.unique < 5 && summary.value.totalRows > 100) {
      newInsights.push({
        type: 'info',
        message: `Column "${col.name}" has low cardinality (${col.unique} unique values)`
      })
    }
  })
  
  // Check for high correlations
  if (topCorrelations.value.length > 0) {
    const highest = topCorrelations.value[0]
    if (Math.abs(highest.value) > 0.9) {
      newInsights.push({
        type: 'important',
        message: `Strong correlation detected between "${highest.col1}" and "${highest.col2}" (${highest.value.toFixed(3)})`
      })
    }
  }
  
  // Check for potential ID columns
  columnStats.value.forEach(col => {
    if (col.unique === summary.value.totalRows && col.dtype !== 'float64') {
      newInsights.push({
        type: 'info',
        message: `Column "${col.name}" might be an ID column (all values unique)`
      })
    }
  })
  
  insights.value = newInsights.slice(0, 6) // Limit to 6 insights
}

// Create data types chart
const createDataTypesChart = () => {
  const typeCount = {}
  columnStats.value.forEach(col => {
    typeCount[col.dtype] = (typeCount[col.dtype] || 0) + 1
  })
  
  const data = [{
    type: 'pie',
    labels: Object.keys(typeCount),
    values: Object.values(typeCount),
    hole: 0.4,
    marker: {
      colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
    }
  }]
  
  const layout = {
    showlegend: true,
    legend: {
      position: 'right'
    },
    margin: { t: 20, b: 20, l: 20, r: 100 }
  }
  
  Plotly.newPlot(dataTypesChart.value, data, layout, { responsive: true })
}

// Create missing data chart
const createMissingDataChart = () => {
  const missingData = columnStats.value.map(col => ({
    name: col.name,
    missing: summary.value.totalRows - col.non_null,
    present: col.non_null
  }))
  
  const data = [
    {
      x: missingData.map(d => d.name),
      y: missingData.map(d => d.present),
      name: 'Present',
      type: 'bar',
      marker: { color: '#10B981' }
    },
    {
      x: missingData.map(d => d.name),
      y: missingData.map(d => d.missing),
      name: 'Missing',
      type: 'bar',
      marker: { color: '#EF4444' }
    }
  ]
  
  const layout = {
    barmode: 'stack',
    xaxis: {
      tickangle: -45
    },
    yaxis: {
      title: 'Row Count'
    },
    margin: { t: 20, b: 100, l: 60, r: 20 },
    showlegend: true,
    legend: {
      x: 0,
      y: 1
    }
  }
  
  Plotly.newPlot(missingDataChart.value, data, layout, { responsive: true })
}

// Refresh sample
const refreshSample = () => {
  fetchSample()
}

// Export summary
const exportSummary = async (format) => {
  try {
    const summaryData = {
      overview: summary.value,
      columnStatistics: columnStats.value,
      insights: insights.value,
      correlations: topCorrelations.value,
      sample: sampleData.value
    }
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(summaryData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `data_summary_${sessionId}.json`
      a.click()
      URL.revokeObjectURL(url)
    } else if (format === 'html') {
      // Generate HTML report
      const html = generateHTMLReport(summaryData)
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `data_summary_${sessionId}.html`
      a.click()
      URL.revokeObjectURL(url)
    } else if (format === 'pdf') {
      // For PDF, we would need a library like jsPDF
      alert('PDF export would require additional library integration')
    }
  } catch (error) {
    console.error('Error exporting summary:', error)
  }
}

// Generate HTML report
const generateHTMLReport = (data) => {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Data Summary Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-label { font-size: 14px; color: #666; }
        .metric-value { font-size: 24px; font-weight: bold; color: #333; }
      </style>
    </head>
    <body>
      <h1>Data Summary Report</h1>
      <p>Generated on ${new Date().toLocaleString()}</p>
      
      <h2>Overview</h2>
      <div>
        <div class="metric">
          <div class="metric-label">Total Rows</div>
          <div class="metric-value">${data.overview.totalRows}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Total Columns</div>
          <div class="metric-value">${data.overview.totalColumns}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Missing Data</div>
          <div class="metric-value">${data.overview.missingPercent}%</div>
        </div>
        <div class="metric">
          <div class="metric-label">Quality Score</div>
          <div class="metric-value">${data.overview.qualityScore}%</div>
        </div>
      </div>
      
      <h2>Column Statistics</h2>
      <table>
        <thead>
          <tr>
            <th>Column</th>
            <th>Type</th>
            <th>Non-Null</th>
            <th>Unique</th>
            <th>Mean/Mode</th>
          </tr>
        </thead>
        <tbody>
          ${data.columnStatistics.map(col => `
            <tr>
              <td>${col.name}</td>
              <td>${col.dtype}</td>
              <td>${col.non_null}</td>
              <td>${col.unique}</td>
              <td>${col.mean !== null ? col.mean.toFixed(2) : col.mode || '-'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      
      <h2>Key Insights</h2>
      <ul>
        ${data.insights.map(insight => `<li>${insight.message}</li>`).join('')}
      </ul>
      
      ${data.correlations.length > 0 ? `
        <h2>Top Correlations</h2>
        <ul>
          ${data.correlations.map(corr => `
            <li>${corr.col1} ↔ ${corr.col2}: ${corr.value.toFixed(3)}</li>
          `).join('')}
        </ul>
      ` : ''}
    </body>
    </html>
  `
}

// Helper functions
const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString()
}

const formatPercent = (num) => {
  if (num === null || num === undefined) return '-'
  return num.toFixed(1)
}

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'number') {
    return val % 1 === 0 ? val.toString() : val.toFixed(2)
  }
  return val.toString()
}

const formatCellValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'number') {
    return val % 1 === 0 ? val.toString() : val.toFixed(2)
  }
  return val.toString().length > 50 ? val.toString().substring(0, 50) + '...' : val.toString()
}

const getTypeClass = (dtype) => {
  const classes = {
    'int64': 'text-blue-600 font-medium',
    'float64': 'text-green-600 font-medium',
    'object': 'text-purple-600 font-medium',
    'bool': 'text-orange-600 font-medium',
    'datetime64': 'text-pink-600 font-medium'
  }
  return classes[dtype] || 'text-gray-600'
}

const getInsightIcon = (type) => {
  const icons = {
    'warning': 'text-yellow-500 text-lg'>⚠️',
    'info': 'text-blue-500 text-lg'>ℹ️',
    'important': 'text-red-500 text-lg'>❗',
    'success': 'text-green-500 text-lg'>✅'
  }
  return icons[type] || 'text-gray-500 text-lg'>•'
}

const getCorrelationClass = (value) => {
  const absValue = Math.abs(value)
  if (absValue > 0.9) return 'text-red-600'
  if (absValue > 0.7) return 'text-orange-600'
  if (absValue > 0.5) return 'text-yellow-600'
  return 'text-gray-600'
}

// Lifecycle
onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.data-summary {
  min-height: 100vh;
  background-color: #f3f4f6;
}
</style>
