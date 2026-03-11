"""
CSV Column Diagnostic Tool
Run this to see what columns are in your CSV file and get mapping suggestions
"""

import pandas as pd
import sys

def diagnose_csv(file_path):
    """Analyze CSV file and suggest column mappings"""
    print("=" * 80)
    print("ADO Audit Log CSV Diagnostic Tool")
    print("=" * 80)
    print()
    
    try:
        # Try to read the CSV
        print(f"Reading file: {file_path}")
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        print(f"✅ Successfully loaded {len(df)} rows")
        print()
        
        # Show columns
        print("COLUMNS FOUND IN YOUR CSV:")
        print("-" * 80)
        for i, col in enumerate(df.columns, 1):
            # Show column name and first non-null value as example
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
            sample_str = str(sample)[:50] + "..." if len(str(sample)) > 50 else str(sample)
            print(f"{i:3d}. {col:40s} | Example: {sample_str}")
        
        print()
        print("=" * 80)
        print("COLUMN MAPPING SUGGESTIONS:")
        print("-" * 80)
        
        # Suggest mappings
        suggestions = {
            'Actor Name': ['actor', 'user', 'name', 'displayname'],
            'Actor Email': ['email', 'upn', 'mail'],
            'Date': ['date', 'time', 'timestamp', 'when'],
            'Event': ['event', 'category', 'type'],
            'Action': ['action', 'operation'],
            'Description': ['description', 'details', 'summary', 'message'],
            'IP Address': ['ip', 'address', 'client']
        }
        
        found_mappings = {}
        for standard_name, keywords in suggestions.items():
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    if standard_name not in found_mappings:
                        found_mappings[standard_name] = col
                        print(f"✅ {standard_name:20s} -> {col}")
                        break
        
        # Show missing mappings
        print()
        print("MISSING MAPPINGS:")
        print("-" * 80)
        for standard_name in suggestions.keys():
            if standard_name not in found_mappings:
                print(f"❌ {standard_name:20s} - Not found (will use empty values)")
        
        print()
        print("=" * 80)
        print("RECOMMENDATIONS:")
        print("-" * 80)
        
        if len(found_mappings) < 4:
            print("⚠️  WARNING: Very few columns were mapped automatically.")
            print("   Your CSV might not be from Azure DevOps audit logs.")
            print()
            print("   To fix this, you can:")
            print("   1. Check that you exported the correct report from ADO")
            print("   2. Add custom mappings to config.py COLUMN_MAPPINGS")
            print("   3. Rename columns in your CSV to match expected names")
        else:
            print("✅ Most columns mapped successfully!")
            print("   The app should work, but some features may be limited")
            print("   if key columns like 'Actor Name' are missing.")
        
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("-" * 80)
        print("1. Review the column mappings above")
        print("2. If mappings look wrong, edit config.py COLUMN_MAPPINGS")
        print("3. Add your column names to the appropriate mapping list")
        print()
        print("Example config.py edit:")
        print("  'Actor Name': ['actordisplayname', 'actorname', 'YOUR_COLUMN_NAME'],")
        print()
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        print()
        print("Common issues:")
        print("- File encoding (try saving as UTF-8)")
        print("- Corrupted file (try re-exporting)")
        print("- Wrong file format (must be CSV)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_csv.py <path_to_csv_file>")
        print()
        print("Example:")
        print("  python diagnose_csv.py audit_log.csv")
        print("  python diagnose_csv.py C:\\Downloads\\audit_log.csv")
    else:
        diagnose_csv(sys.argv[1])
