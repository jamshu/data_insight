# 📦 Stock Movement Processing Feature

## Overview

The Stock Movement Processing feature allows you to process and analyze stock movement Excel reports with automatic calculation of UOM Done quantities and running balances. This feature is designed specifically for warehouse and inventory management workflows.

## ✨ Key Features

### 📋 File Validation
- **Automatic Validation**: Validates uploaded Excel files to ensure they contain all required stock movement columns
- **Required Columns**: Date, Reference, Product, From, To, Done, Unit of Measure, Status
- **User Feedback**: Clear feedback on missing columns or invalid file structure

### 🔢 UOM Processing
- **Unit Conversion**: Automatically converts different Units of Measure (UOM) to standard units
- **Configurable Mappings**: Support for custom UOM mappings (e.g., Cartons-24 = 24 units)
- **Smart Detection**: Auto-detects common UOM patterns in your data

### ➕➖ Sign Calculation
- **Location-Based Logic**: Automatically determines positive/negative movements based on source and destination locations
- **Inbound Movements**: When destination matches your facility location (positive sign)
- **Outbound Movements**: When source matches your facility location (negative sign)

### 📊 Advanced Calculations

#### UOM Done Quantity
```
UOM_Done_Qty = Quantity × UOM_Units × Sign
```

**Example:**
- Quantity: 2 Cartons-24
- UOM_Units: 24 (from mapping)
- Sign: +1 (inbound to factory)
- **Result**: 2 × 24 × 1 = 48 units

#### Running Balance
```
Running_Balance = Cumulative sum of UOM_Done_Qty (sorted by date)
```

### 📈 Visual Analytics
- **Interactive Charts**: Running balance trend visualization
- **Summary Statistics**: Total inbound/outbound movements and final balance
- **Color-Coded Display**: Green for positive, red for negative values

### 💾 Excel Export
- **Enhanced Formatting**: Professional Excel output with highlighted calculated columns
- **Original Data Preserved**: All original columns maintained with new calculations appended
- **Ready for Analysis**: Formatted for further analysis in Excel or other tools

## 🚀 How to Use

### Step 1: Upload & Validate
1. Upload your stock movement Excel file
2. Click "Validate Stock Movement File"
3. Ensure validation passes before proceeding

### Step 2: Configure Processing
1. **UOM Column**: Select the column containing unit of measure data
2. **From Location**: Select the source location column
3. **To Location**: Select the destination location column  
4. **Quantity Column**: Select the quantity column
5. **Check Location**: Enter your facility location (e.g., "JDFCW/Jeddah Factory")
6. **UOM Mappings**: Add mappings for your units (e.g., Cartons-24 → 24)

### Step 3: Process & Analyze
1. Click "Process Stock Movement"
2. Review the calculated columns and running balance
3. Use the interactive chart to visualize trends
4. Export the enhanced Excel file if needed

## 📋 Sample Configuration

### UOM Mappings
```
Cartons-24 → 24 units
Cartons-50 → 50 units
Units → 1 unit
```

### Location Logic
```
Check Location: "JDFCW/Jeddah Factory"

Examples:
From: "Partners/Customers" → To: "JDFCW/Jeddah Factory" = +Inbound
From: "JDFCW/Jeddah Factory" → To: "Partners/Customers" = -Outbound
```

## 🎯 Sample Results

Given the following stock movements:

| Date | From | To | Done | UOM | UOM_Units | Sign | UOM_Done_Qty | Running_Balance |
|------|------|----|----- |----|-----------|------|--------------|-----------------|
| 12/19 | Customers | Factory | 48 | Units | 1 | +48 | 48 | 48 |
| 12/22 | Factory | Customers | 0.99 | Cartons-24 | 24 | -0.99 | -23.8 | 24.2 |
| 12/23 | Transfer | Factory | 1 | Cartons-24 | 24 | +1 | 24 | 48.2 |

## 🔧 Technical Implementation

### Backend Processing
- **Pandas Integration**: Efficient data processing using pandas
- **Excel Export**: Professional formatting with openpyxl
- **Input Validation**: Comprehensive file structure validation

### Frontend Features
- **Vue.js 3**: Reactive UI with Composition API
- **Real-time Validation**: Immediate feedback on file uploads
- **Interactive Tables**: Paginated data display with search/sort
- **Chart Integration**: Plotly.js for interactive visualizations

### API Endpoints
- `GET /api/stock-movement/validate/{session_id}` - Validate file structure
- `POST /api/stock-movement/process` - Process stock movements
- `POST /api/stock-movement/export/{session_id}` - Export enhanced Excel
- `GET /api/stock-movement/columns/{session_id}` - Get available columns

## 📊 Column Explanations

| Column | Description | Calculation |
|--------|-------------|-------------|
| **UOM_Qty_Done** | Units per UOM item | From UOM mappings |
| **Sign** | Direction indicator | Based on From/To locations |
| **UOM_Done_Qty** | Total units moved | Quantity × UOM_Units × Sign |
| **Running_Balance** | Cumulative balance | Sum of UOM_Done_Qty over time |

## ⚠️ Important Notes

1. **File Format**: Only Excel files (.xlsx, .xls) with the required column structure are supported
2. **Date Sorting**: Data is automatically sorted by date for accurate running balance calculation
3. **Location Matching**: Location matching is case-sensitive and uses substring matching
4. **UOM Mappings**: Ensure all UOM values in your data have corresponding mappings for accurate conversion

## 🔍 Troubleshooting

### Common Issues

**Validation Failed**
- Check that all required columns are present
- Ensure column names match exactly (case-sensitive)

**Incorrect Running Balance**
- Verify UOM mappings are correct
- Check that the location matching logic is appropriate for your data
- Ensure the date column contains valid dates

**Export Issues**
- Make sure the processing completed successfully
- Check that the uploads directory is accessible
- Verify your browser allows file downloads

## 📞 Support

For additional support or feature requests, please refer to the main application documentation or contact your system administrator.
