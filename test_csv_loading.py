"""
Test script to see what the app is actually loading from your CSV
"""

import pandas as pd
import sys

def test_load(file_path):
    print("=" * 80)
    print("Testing CSV Load")
    print("=" * 80)
    print()
    
    # Try the same loading strategy as the app
    strategies = [
        {'engine': 'c', 'encoding': 'utf-8', 'on_bad_lines': 'skip'},
        {'engine': 'python', 'encoding': 'utf-8', 'quoting': 1, 'doublequote': True},
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"Strategy {i}: {strategy}")
        try:
            df = pd.read_csv(file_path, **strategy)
            print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
            print()
            print("Columns:", list(df.columns))
            print()
            print("First 3 rows of key columns:")
            print("-" * 80)
            
            # Show the columns that should have user names
            if 'Actor Name' in df.columns:
                print(f"Actor Name column (first 3):")
                for val in df['Actor Name'].head(3):
                    print(f"  - {val}")
            
            if 'Event' in df.columns:
                print(f"\nEvent column (first 3):")
                for val in df['Event'].head(3):
                    print(f"  - {val}")
            
            if 'Action' in df.columns:
                print(f"\nAction column (first 3):")
                for val in df['Action'].head(3):
                    print(f"  - {val}")
            
            print()
            print("Full first row:")
            print(df.iloc[0].to_dict())
            
            break
        except Exception as e:
            print(f"❌ Failed: {e}")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_csv_loading.py <path_to_csv>")
    else:
        test_load(sys.argv[1])
