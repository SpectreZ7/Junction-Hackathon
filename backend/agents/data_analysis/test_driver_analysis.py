#!/usr/bin/env python3
"""
Test script to demonstrate driver-specific analysis
"""

from agents.rides_analysis_agent import analyze_driver, get_driver_summary, data

def main():
    print("=== Driver Analysis Demo ===")
    
    # Show overview
    get_driver_summary()
    
    print("\n" + "="*60 + "\n")
    
    # Analyze top 3 most active drivers
    top_drivers = data['driver_id'].value_counts().head(3).index.tolist()
    
    for i, driver in enumerate(top_drivers, 1):
        print(f"Analysis #{i}: Most Active Driver {driver}")
        print("-" * 40)
        analyze_driver(driver)
        if i < len(top_drivers):
            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()