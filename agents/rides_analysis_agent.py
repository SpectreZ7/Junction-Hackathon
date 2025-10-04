# Analyzes data file for rides
#  an AI "shadow driver" that learns a specific earner's unique patterns, then simulates their optimal week.
import datetime
import pandas as pd
# takes data from rides_trips data sheet tablyzes data file for rides
#  an AI “shadow driver” that learns a specific earner’s unique patterns, then simulates their optimal week.

# takes data from rides_trips data sheet tab
data = pd.read_excel("data/uber_mock_data.xlsx", sheet_name="rides_trips")
driver_ids = data['driver_id'].unique()

def get_driver_summary():
    '''Display summary of all available drivers'''
    print(f"Total number of drivers in dataset: {len(driver_ids)}")
    print("Sample of driver IDs:", driver_ids[:10])
    
    # Show ride counts per driver
    driver_ride_counts = data['driver_id'].value_counts().head(10)
    print("\nTop 10 drivers by ride count:")
    for driver, count in driver_ride_counts.items():
        print(f"  {driver}: {count} rides")
    return driver_ids

def analyze_driver(driver_id):
    '''Comprehensive analysis for a specific driver'''
    if driver_id not in driver_ids:
        print(f"Error: Driver {driver_id} not found in dataset.")
        print("Available drivers:", driver_ids[:10], "...")
        return
    
    print(f"Analyzing driver: {driver_id}")
    print(f"Total rides for this driver: {len(data[data['driver_id'] == driver_id])}")
    print("-" * 50)

    # Analyze each day of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days:
        rides_count = days_of_the_week(data, driver_id, day)
        print(f"Number of rides on {day}: {rides_count}")

    print("-" * 50)

    # Earnings analysis
    avg_earnings = earnings_per_minute(data, driver_id)
    for earning_stat in avg_earnings:
        print(earning_stat)

    print("-" * 50)

    # Peak hours analysis
    busiest_hour = peak_hours(data, driver_id)
    if busiest_hour is not None:
        print(f"Busiest hour of the day: {busiest_hour}:00 ({busiest_hour % 12 if busiest_hour % 12 != 0 else 12}{'PM' if busiest_hour >= 12 else 'AM'})")
    else:
        print("No rides found for this driver")

# Example: analyze the first driver in the list
driver_id = driver_ids[0]

def days_of_the_week(data, driver_id, week_day):
    '''Analyze rides by day of the week for a specific driver.
    Input: data from rides_trips sheet, driver_id, and day of the week to analyze
    Output: number of rides on that day of the week for that driver
    e.g. Input: data, 'E10111', 'Monday'
         Output: 12
    '''
    # Filter data for the specific driver
    driver_data = data[data['driver_id'] == driver_id].copy()
    
    # Convert start_time to datetime if it's not already
    driver_data['start_time'] = pd.to_datetime(driver_data['start_time'])
    
    # Filter by day of the week
    day_data = driver_data[driver_data['start_time'].dt.day_name() == week_day]
    return len(day_data)


def earnings_per_minute(data, driver_id):
    '''Analyze earnings per minute for rides for a specific driver.
    Input: data from rides_trips sheet and driver_id
    Output: average earnings per minute for that driver
    e.g. Input: data, 'E10111'
         Output: tuple of earnings per minute statistics
    '''
    # Filter data for the specific driver
    driver_data = data[data['driver_id'] == driver_id]
    
    # Convert datetime columns and calculate duration
    driver_data = driver_data.copy()  # Avoid SettingWithCopyWarning
    driver_data['start_time'] = pd.to_datetime(driver_data['start_time'])
    driver_data['end_time'] = pd.to_datetime(driver_data['end_time'])
    driver_data['ride_duration'] = (driver_data['end_time'] - driver_data['start_time']).dt.total_seconds() / 60
    
    # Use the correct column name for fare (it's 'fare_amount' not 'fare')
    mean_earnings_per_minute = (driver_data['fare_amount'] / driver_data['ride_duration']).mean()
    
    # Long rides (> 30 min)
    long_rides = driver_data[driver_data['ride_duration'] > 30]
    earnings_per_minute_long_rides = (long_rides['fare_amount'] / long_rides['ride_duration']).mean() if len(long_rides) > 0 else 0
    
    # Short rides (< 15 min)
    short_rides = driver_data[driver_data['ride_duration'] < 15]
    earnings_per_minute_short_rides = (short_rides['fare_amount'] / short_rides['ride_duration']).mean() if len(short_rides) > 0 else 0
    
    return f"Avg earnings per minute (all rides): {mean_earnings_per_minute:.2f}", f"Avg earnings per minute (rides > 30 min): {earnings_per_minute_long_rides:.2f}", f"Avg earnings per minute (rides < 15 min): {earnings_per_minute_short_rides:.2f}"


def peak_hours(data, driver_id):
    '''Analyze peak hours for rides for a specific driver.
    Input: data from rides_trips sheet and driver_id
    Output: hour of the day with the highest number of rides for that driver
    e.g. Input: data, 'E10111'
         Output: 18 (for 6 PM)
    '''
    # Filter data for the specific driver
    driver_data = data[data['driver_id'] == driver_id]
    
    # Convert start_time to datetime if it's not already
    driver_data = driver_data.copy()  # Avoid SettingWithCopyWarning
    driver_data['start_time'] = pd.to_datetime(driver_data['start_time'])
    driver_data['ride_hour'] = driver_data['start_time'].dt.hour
    
    # Return the most common hour, or None if no rides
    if len(driver_data) > 0:
        return driver_data['ride_hour'].mode()[0]
    else:
        return None

def create_digital_twin(driver_id: str):
    """Create and run Digital Twin analysis for a driver"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from digital_twin_agent import DigitalTwinAgent
        
        print(f"🤖 Creating Digital Twin for {driver_id}...")
        agent = DigitalTwinAgent()
        
        # Learn patterns
        profile = agent.learn_driver_patterns(driver_id)
        
        # Run optimization
        optimization = agent.simulate_optimal_week(profile)
        
        # Display results
        agent.visualize_driver_profile(profile)
        agent.print_optimization_results(optimization)
        
        return profile, optimization
        
    except ImportError as e:
        print(f"❌ Digital Twin Agent not available: {e}")
        print("Make sure digital_twin_agent.py is in the same directory.")
    except Exception as e:
        print(f"❌ Error creating Digital Twin: {e}")

# Example usage
if __name__ == "__main__":
    # Show overview of available drivers
    get_driver_summary()
    print("\n" + "="*60 + "\n")
    
    # Analyze a specific driver
    analyze_driver(driver_id)
    
    print("\n" + "="*60 + "\n")
    print("🤖 DIGITAL TWIN AVAILABLE!")
    print("To create AI shadow driver, call: create_digital_twin('DRIVER_ID')")
    print(f"Example: create_digital_twin('{driver_id}')")
    print("\n" + "="*60 + "\n")
    print("To analyze a different driver, call: analyze_driver('DRIVER_ID')")
    print("Example: analyze_driver('E10152')")