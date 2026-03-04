"""
CORRECTED Social Media Metrics Tracker
Fixed alignment issue - values now properly match column headers
Period_Text column removed, only Period_YYYYMM remains
"""

import pdfplumber
import csv
import re
import os


def parse_date_to_yyyymm(date_string):
    """
    Convert "Jan 01 - Jan 31, 2026" to "202601"
    """
    
    if not date_string:
        return None
    
    # Extract the end date: "Jan 31, 2026"
    match = re.search(r'-\s*(\w{3})\s+\d{1,2},?\s*(\d{4})', date_string)
    
    if match:
        month_str = match.group(1)
        year = match.group(2)
        
        # Convert month name to number
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        month_num = month_map.get(month_str, '01')
        return f"{year}{month_num}"
    
    return None


def extract_metrics_from_pdf(pdf_path):
    """
    Extract metrics from a single PDF
    Returns: (period_yyyymm, metrics_dict)
    """
    
    metrics_dict = {}
    report_date = None
    
    with pdfplumber.open(pdf_path) as pdf:
        # Get report date from page 1
        page1 = pdf.pages[0]
        text1 = page1.extract_text()
        
        # Extract date
        date_match = re.search(r'(\w{3}\s+\d{1,2}\s*-\s*\w{3}\s+\d{1,2},?\s*\d{4})', text1)
        if date_match:
            report_date = date_match.group(1)
        
        # Extract metrics from page 2
        page = pdf.pages[1]
        tables = page.extract_tables()
        
        if tables:
            table = tables[0]
            
            for row in table:
                for cell in row:
                    if cell:
                        parts = cell.strip().split('\n')
                        
                        # Find the value (number)
                        value_idx = None
                        for i, part in enumerate(parts):
                            clean_part = part.replace(',', '').replace('%', '')
                            if re.match(r'^\d+\.?\d*$', clean_part):
                                value_idx = i
                                break
                        
                        if value_idx is not None:
                            metric_name = ' '.join(parts[:value_idx]).replace('…', '').strip()
                            value = parts[value_idx].replace(',', '').replace('%', '')
                            
                            if metric_name and value:
                                if metric_name not in metrics_dict:
                                    metrics_dict[metric_name] = value
    
    period_yyyymm = parse_date_to_yyyymm(report_date)
    
    return period_yyyymm, metrics_dict


def create_or_update_csv(csv_path, period_yyyymm, metrics_dict):
    """
    Create a new CSV or append to existing one
    """
    
    # Define standard column order - these match the extracted metric names
    all_possible_metrics = [
        'Average post engageme',
        'Followers',
        'Inbound messages',
        'New followers',
        'Page & profile impressions',
        'Page & profile reach',
        'Post comments & replies',
        'Post impressions',
        'Post link clicks',
        'Post reach',
        'Post reactions & likes',
        'Post video views',
        'Posts'
    ]
    
    file_exists = os.path.exists(csv_path)
    
    if not file_exists:
        # Create new CSV with headers
        # ONLY Period_YYYYMM, no Period_Text
        headers = ['Period_YYYYMM'] + all_possible_metrics
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        print(f"✓ Created new CSV with {len(headers)} columns")
    
    # Build the values row - ONLY period_yyyymm, no original_period
    values = [period_yyyymm]
    for metric in all_possible_metrics:
        values.append(metrics_dict.get(metric, ''))
    
    # Append the new row
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(values)
    
    print(f"✓ Added row for period: {period_yyyymm}")
    
    return values


def validate_alignment(csv_path):
    """
    Show the exact alignment to verify correctness
    """
    
    print("\n" + "=" * 70)
    print("ALIGNMENT VERIFICATION:")
    print("=" * 70)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        print(f"\nHeaders ({len(headers)} columns):")
        for i, header in enumerate(headers):
            print(f"  {i:2d}. {header}")
        
        print(f"\nData:")
        for row_num, row in enumerate(reader, 1):
            print(f"\n  Row {row_num}:")
            for i in range(len(headers)):
                if i < len(row):
                    print(f"    {headers[i]:<40} = {row[i]}")
                else:
                    print(f"    {headers[i]:<40} = [MISSING]")
    
    print("=" * 70)


if __name__ == "__main__":
    pdf_path = "/mnt/user-data/uploads/custom_report_3_2026-01-01_to_2026-01-31_created_on_20260212T2106Z.pdf"
    output_csv = "/home/claude/social_media_corrected.csv"
    
    print("="*70)
    print("CORRECTED SOCIAL MEDIA METRICS TRACKER")
    print("="*70)
    
    # Extract from PDF
    period_yyyymm, metrics_dict = extract_metrics_from_pdf(pdf_path)
    
    print(f"\nPeriod: {period_yyyymm}")
    print(f"Metrics extracted: {len(metrics_dict)}")
    
    print("\nMetrics and values:")
    for metric, value in metrics_dict.items():
        print(f"  {metric:<40} = {value}")
    
    # Create/update CSV
    print("\n" + "=" * 70)
    create_or_update_csv(output_csv, period_yyyymm, metrics_dict)
    
    # Validate alignment
    validate_alignment(output_csv)
    
    print("\n✓ CSV created successfully!")
    print(f"✓ File: {output_csv}")
