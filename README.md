# 🚀 Universal Data Analytics Platform

A modern, full-stack web application for comprehensive data analysis and visualization. Built with Vue.js 3, FastAPI, and Pandas, this platform provides powerful tools for exploring, analyzing, and visualizing data from CSV and Excel files.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009485.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Key Features

### 📊 Universal Data Processing
- **Any Format**: Accepts CSV, Excel (xlsx, xls) files
- **Fast Processing**: Uses Pandas for robust data operations
- **Large Files**: Handles files up to 100MB efficiently
- **Smart Detection**: Automatically detects data types and patterns
- **Drag & Drop**: Intuitive file upload interface

### 🎯 Automated Analysis
- **Statistical Summary**: Mean, median, std dev, percentiles for all numeric columns
- **Pattern Detection**: Identifies missing data, outliers, and anomalies
- **Correlation Analysis**: Automatic correlation matrix for numeric variables
- **Data Quality**: Detects duplicates, single-value columns, and data issues
- **Group By Analysis**: Interactive group-by with multiple aggregation functions
- **Click-through Filtering**: Navigate from grouped data to detailed records

### 📈 Interactive Visualizations
- **Auto Insights**: Generates appropriate charts based on data types
- **Multiple Chart Types**: Scatter, histogram, box plot, heatmap, line, bar, pie
- **Plotly Integration**: Interactive, zoomable, downloadable charts
- **Custom Visualizations**: Build your own charts with column selection
- **Dark Mode**: Full dark mode support with system preference detection
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 💾 Export Capabilities
- **Multiple Formats**: Export to CSV, JSON, or Excel
- **Filtered Exports**: Export filtered subsets of data
- **Comprehensive Reports**: Generate full analysis reports
- **Data Samples**: Preview and download data samples
- **Session Management**: Maintain multiple analysis sessions

## 🏗️ Architecture

```
data_insights_platform/
│
├── backend/                    # FastAPI backend
│   ├── api/
│   │   └── routers/           # API route handlers
│   │       ├── upload.py      # File upload handling
│   │       ├── analysis.py    # Data analysis endpoints
│   │       ├── sessions.py    # Session management
│   │       └── export.py      # Data export endpoints
│   ├── services/              # Business logic
│   │   └── data_processor.py # Pandas data processing
│   ├── uploads/               # Uploaded files storage
│   ├── main.py               # FastAPI application entry point
│   └── requirements.txt       # Python dependencies
│
└── frontend/                   # Vue.js 3 frontend
    ├── src/
    │   ├── components/        # Reusable Vue components
    │   │   ├── FileUploadModal.vue
    │   │   └── NotificationToast.vue
    │   ├── views/             # Page components
    │   │   ├── Dashboard.vue
    │   │   ├── Analysis.vue
    │   │   └── Settings.vue
    │   ├── utils/             # Utility functions
    │   ├── App.vue           # Root component
    │   └── main.js           # Application entry point
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite configuration
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pandas**: Powerful data manipulation and analysis library
- **NumPy**: Numerical computing library
- **Uvicorn**: Lightning-fast ASGI server
- **Python 3.9+**: Core programming language

### Frontend
- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **Vite**: Next-generation frontend build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Plotly.js**: Interactive visualization library
- **Axios**: Promise-based HTTP client
- **Vue Router**: Official router for Vue.js

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn package manager

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```bash
   .\.venv\Scripts\activate
   ```
   
   macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

The application will be available at `http://localhost:3000`

## 📡 API Documentation

### Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI documentation

### Main Endpoints

#### 📤 Upload
- `POST /api/upload/` - Upload CSV or Excel file
- `GET /api/upload/sessions` - List active sessions
- `DELETE /api/upload/{session_id}` - Delete session

#### 📊 Analysis
- `GET /api/analysis/{session_id}/summary` - Complete data summary
- `GET /api/analysis/{session_id}/columns` - Column-wise analysis
- `GET /api/analysis/{session_id}/correlations` - Correlation matrix
- `GET /api/analysis/{session_id}/distribution/{column}` - Column distribution
- `GET /api/analysis/{session_id}/patterns` - Pattern detection

#### 📈 Visualization
- `GET /api/visualization/{session_id}/chart/{chart_type}` - Generate charts
- `GET /api/visualization/{session_id}/insights` - Auto-generated insights

#### 💾 Export
- `GET /api/export/{session_id}/download` - Download data (CSV/JSON/Parquet)
- `GET /api/export/{session_id}/report` - Generate analysis report

## 🔄 Workflow

1. **Upload**: Upload your CSV or Excel file
2. **Analyze**: Get instant statistical analysis and patterns
3. **Visualize**: View auto-generated charts or create custom ones
4. **Export**: Download processed data or comprehensive reports

## 📊 Example Usage

### Using Python Requests

```python
import requests

# Upload file
with open('data.csv', 'rb') as f:
    response = requests.post('http://localhost:8000/api/upload/', 
                            files={'file': f})
    session_id = response.json()['session_id']

# Get analysis
analysis = requests.get(f'http://localhost:8000/api/analysis/{session_id}/summary')
print(analysis.json())

# Generate visualization
viz = requests.get(f'http://localhost:8000/api/visualization/{session_id}/insights')
insights = viz.json()

# Export data
export = requests.get(f'http://localhost:8000/api/export/{session_id}/download?format=csv')
```

### Using cURL

```bash
# Upload file
curl -X POST "http://localhost:8000/api/upload/" \
  -H "accept: application/json" \
  -F "file=@data.csv"

# Get summary (replace SESSION_ID with actual ID)
curl "http://localhost:8000/api/analysis/SESSION_ID/summary"
```

## 🎨 Frontend Features

The Vue.js frontend provides:
- **Drag-and-drop file upload**: Intuitive file upload with progress tracking
- **Interactive dashboard**: Real-time updates and session management
- **Beautiful visualizations**: Interactive charts with Plotly.js
- **Group By Analysis**: Interactive data grouping with drill-down capability
- **Data Preview**: Paginated table view with filtering
- **Export functionality**: Download data in multiple formats
- **Dark Mode**: System-aware theme switching
- **Responsive design**: Optimized for all devices

## 🚀 Performance

- **File Size**: Handles up to 100MB files
- **Processing Speed**: 10-100x faster than Pandas
- **Concurrent Users**: Supports multiple sessions
- **Memory Efficient**: Optimized memory usage with Polars

## 🔒 Security Features

- File type validation
- File size limits
- Session isolation
- Secure file storage
- Input sanitization

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **File Upload Fails**
   - Check file size (max 100MB)
   - Ensure CSV/Excel format
   - Verify file isn't corrupted

3. **Polars Installation Issues**
   ```bash
   pip install polars --no-binary polars
   ```

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI and Polars**
