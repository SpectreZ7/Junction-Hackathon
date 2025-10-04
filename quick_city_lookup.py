#!/usr/bin/env python3
"""
Quick city lookup - Pass city ID as command line argument

Usage:
    python quick_city_lookup.py 3        # Get top drivers for City 3
    python quick_city_lookup.py 0        # Get top drivers for all cities
"""

import sys
from agents.driver_prioritization_agent import DriverPrioritizationAgent

def main():
    # Get city ID from command line
    if len(sys.argv) < 2:
        print("❌ Error: Please provide city ID")
        print("\nUsage:")
        print("  python quick_city_lookup.py 3    # City 3")
        print("  python quick_city_lookup.py 0    # All cities")
        print("\nAvailable cities: 0 (all), 1, 2, 3, 4, 5")
        sys.exit(1)
    
    try:
        city_input = int(sys.argv[1])
    except ValueError:
        print("❌ Error: City ID must be a number (0-5)")
        sys.exit(1)
    
    if city_input < 0 or city_input > 5:
        print("❌ Error: City ID must be 0-5")
        sys.exit(1)
    
    # Get number of drivers (optional argument)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # Initialize agent
    print(f"\n🏙️  Analyzing City {city_input if city_input > 0 else 'All'}...\n")
    
    if city_input == 0:
        agent = DriverPrioritizationAgent()
    else:
        agent = DriverPrioritizationAgent(city_id=city_input)
    
    # Get top drivers
    top_drivers = agent.get_top_drivers(n=n)
    
    # Print results
    print(f"\n🏆 TOP {n} DRIVERS:")
    print(f"{'Rank':<6} {'Driver ID':<12} {'Priority':<10} {'Rating':<8} {'Exp Boost':<12}")
    print("-"*60)
    
    for driver in top_drivers:
        print(f"#{driver.rank:<5} {driver.earner_id:<12} {driver.overall_priority_score:<10.4f} "
              f"{driver.raw_rating:<8.2f} {driver.experience_boost:<12.1%}")
    
    print(f"\n✅ Best driver in this city: {top_drivers[0].earner_id}")

if __name__ == "__main__":
    main()

