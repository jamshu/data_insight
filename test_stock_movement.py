#!/usr/bin/env python3
"""
Test script for stock movement processing functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime

def test_stock_movement_processing():
    """Test the stock movement processing logic"""
    
    # Load the sample Excel file
    file_path = "Product Moves (Stock Move Line) (stock.move.line).xlsx"
    df = pd.read_excel(file_path)
    
    print("Original Data:")
    print("=" * 50)
    print(f"Columns: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    print("\nData:")
    print(df)
    print("\n")
    
    # Test validation
    required_columns = {'Date', 'Reference', 'Product', 'From', 'To', 'Done', 'Unit of Measure', 'Status'}
    existing_columns = set(df.columns)
    missing_columns = required_columns - existing_columns
    is_valid = len(missing_columns) == 0
    
    print(f"Validation Result: {is_valid}")
    if not is_valid:
        print(f"Missing columns: {missing_columns}")
        return
    
    # Configuration
    config = {
        'uom_column': 'Unit of Measure',
        'location_from_column': 'From',
        'location_to_column': 'To',
        'quantity_column': 'Done',
        'check_location': 'JDFCW/Jeddah Factory',
        'uom_mappings': [
            {'uom_name': 'Cartons-24', 'units': 24},
            {'uom_name': 'Units', 'units': 1}
        ]
    }
    
    # Create UOM mapping dictionary
    uom_dict = {mapping['uom_name']: mapping['units'] for mapping in config['uom_mappings']}
    print(f"UOM Mappings: {uom_dict}")
    
    # Process UOM Qty column
    def convert_uom(value):
        if pd.isna(value):
            return 1
        value_str = str(value)
        for uom_name, units in uom_dict.items():
            if uom_name in value_str:
                return units
        return 1
    
    df['UOM_Qty_Done'] = df[config['uom_column']].apply(convert_uom)
    
    # Process Sign column based on location (To/From)
    def calculate_sign(row):
        from_location = str(row[config['location_from_column']])
        to_location = str(row[config['location_to_column']])
        quantity = row[config['quantity_column']]
        
        # If destination is the check location, it's an inbound movement (+)
        if config['check_location'] in to_location:
            return quantity
        # If source is the check location, it's an outbound movement (-)
        elif config['check_location'] in from_location:
            return -quantity
        # For other movements, use destination as positive
        else:
            return quantity
    
    df['Sign'] = df.apply(calculate_sign, axis=1)
    
    # Apply UOM conversion to Sign column (Cartons x Units x Sign = UOM_Done_Qty)
    df['UOM_Done_Qty'] = df['Sign'] * df['UOM_Qty_Done']
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values(by='Date')
    
    # Calculate running balance
    df['Running_Balance'] = df['UOM_Done_Qty'].cumsum()
    
    print("Processed Data:")
    print("=" * 50)
    print(df[['Date', 'Reference', 'Product', 'From', 'To', 'Done', 'Unit of Measure', 'UOM_Qty_Done', 'Sign', 'UOM_Done_Qty', 'Running_Balance']])
    
    # Calculate summary statistics
    summary = {
        'total_rows': len(df),
        'total_inbound': float(df[df['Sign'] > 0]['UOM_Done_Qty'].sum()),
        'total_outbound': float(df[df['Sign'] < 0]['UOM_Done_Qty'].sum()),
        'final_balance': float(df['Running_Balance'].iloc[-1]) if len(df) > 0 else 0,
        'unique_from_locations': df[config['location_from_column']].nunique(),
        'unique_to_locations': df[config['location_to_column']].nunique(),
        'unique_uoms': df[config['uom_column']].nunique()
    }
    
    print("\nSummary:")
    print("=" * 50)
    for key, value in summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_stock_movement_processing()
