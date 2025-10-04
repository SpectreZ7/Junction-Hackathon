#!/usr/bin/env python3
"""
Driver Digital Twin Agent 🧍‍♂️➕🤖

Build an AI "shadow driver" that learns a specific earner's unique patterns, 
then simulates their optimal week for maximum earnings.

Uses historical data to understand:
- When they usually drive
- Which zones they prefer  
- How they respond to surge, bonuses, fatigue
- Their efficiency patterns

Then runs "what if" simulations to optimize their schedule.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DriverProfile:
    """Driver's behavioral profile learned from historical data"""
    driver_id: str
    preferred_hours: List[int]
    peak_days: List[str]
    avg_earnings_per_hour: float
    surge_responsiveness: float
    fatigue_threshold: int  # hours before efficiency drops
    preferred_zones: List[int]
    incentive_completion_rate: float
    consistency_score: float


class DigitalTwinAgent:
    """AI Shadow Driver that learns and optimizes driver behavior"""
    
    def __init__(self, data_path: str = "data/uber_mock_data.xlsx"):
        """Initialize with all necessary data"""
        # Load all data sheets
        self.rides_data = pd.read_excel(data_path, sheet_name="rides_trips")
        self.earnings_data = pd.read_excel(data_path, sheet_name="earnings_daily") 
        self.incentives_data = pd.read_excel(data_path, sheet_name="incentives_weekly")
        self.surge_data = pd.read_excel(data_path, sheet_name="surge_by_hour")
        
        # Preprocess data
        self._preprocess_data()
        
    def _preprocess_data(self):
        """Clean and prepare data for analysis"""
        # Convert datetime columns
        self.rides_data['start_time'] = pd.to_datetime(self.rides_data['start_time'])
        self.rides_data['end_time'] = pd.to_datetime(self.rides_data['end_time'])
        self.rides_data['date'] = self.rides_data['start_time'].dt.date
        self.rides_data['hour'] = self.rides_data['start_time'].dt.hour
        self.rides_data['day_name'] = self.rides_data['start_time'].dt.day_name()
        
        self.earnings_data['date'] = pd.to_datetime(self.earnings_data['date'])
        self.earnings_data['day_name'] = self.earnings_data['date'].dt.day_name()
        
        # Calculate ride duration and earnings per hour
        self.rides_data['duration_mins'] = (self.rides_data['end_time'] - self.rides_data['start_time']).dt.total_seconds() / 60
        self.rides_data['earnings_per_hour'] = (self.rides_data['net_earnings'] * 60) / self.rides_data['duration_mins']
        
    def learn_driver_patterns(self, driver_id: str) -> DriverProfile:
        """Learn comprehensive patterns from driver's historical data"""
        
        # Filter data for specific driver
        driver_rides = self.rides_data[self.rides_data['driver_id'] == driver_id].copy()
        driver_earnings = self.earnings_data[self.earnings_data['earner_id'] == driver_id].copy()
        driver_incentives = self.incentives_data[self.incentives_data['earner_id'] == driver_id].copy()
        
        if len(driver_rides) == 0:
            raise ValueError(f"No data found for driver {driver_id}")
            
        # 1. Learn preferred hours (when they're most active)
        hourly_activity = driver_rides['hour'].value_counts().sort_index()
        preferred_hours = hourly_activity.nlargest(8).index.tolist()  # Top 8 active hours
        
        # 2. Learn peak days
        daily_activity = driver_rides['day_name'].value_counts()
        peak_days = daily_activity.nlargest(3).index.tolist()  # Top 3 days
        
        # 3. Calculate average earnings per hour
        avg_earnings_per_hour = driver_rides['earnings_per_hour'].mean()
        
        # 4. Measure surge responsiveness (correlation between surge and activity)
        surge_response = self._calculate_surge_responsiveness(driver_rides)
        
        # 5. Estimate fatigue threshold (when efficiency starts dropping)
        fatigue_threshold = self._estimate_fatigue_threshold(driver_rides)
        
        # 6. Identify preferred zones
        preferred_zones = driver_rides['pickup_hex_id9'].value_counts().head(5).index.tolist()
        
        # 7. Calculate incentive completion rate
        if len(driver_incentives) > 0:
            incentive_completion_rate = driver_incentives['achieved'].mean()
        else:
            incentive_completion_rate = 0.0
            
        # 8. Calculate consistency score (how regular their patterns are)
        consistency_score = self._calculate_consistency(driver_rides)
        
        return DriverProfile(
            driver_id=driver_id,
            preferred_hours=preferred_hours,
            peak_days=peak_days,
            avg_earnings_per_hour=avg_earnings_per_hour,
            surge_responsiveness=surge_response,
            fatigue_threshold=fatigue_threshold,
            preferred_zones=preferred_zones,
            incentive_completion_rate=incentive_completion_rate,
            consistency_score=consistency_score
        )
    
    def _calculate_surge_responsiveness(self, driver_rides: pd.DataFrame) -> float:
        """Calculate how responsive driver is to surge pricing"""
        if len(driver_rides) == 0:
            return 0.0
            
        # Merge with surge data
        hourly_rides = driver_rides.groupby(['hour']).size().reset_index(name='ride_count')
        surge_merged = pd.merge(hourly_rides, self.surge_data, left_on='hour', right_on='hour', how='left')
        
        if len(surge_merged) > 1:
            correlation = surge_merged['ride_count'].corr(surge_merged['surge_multiplier'])
            return correlation if not pd.isna(correlation) else 0.0
        return 0.0
    
    def _estimate_fatigue_threshold(self, driver_rides: pd.DataFrame) -> int:
        """Estimate when driver efficiency starts dropping due to fatigue"""
        # Group by date and calculate daily working hours and efficiency
        daily_stats = driver_rides.groupby('date').agg({
            'hour': lambda x: x.max() - x.min() + 1,  # Working hours span
            'earnings_per_hour': 'mean'
        }).reset_index()
        
        daily_stats.columns = ['date', 'working_hours', 'avg_efficiency']
        
        # Find the point where longer hours correlate with lower efficiency
        if len(daily_stats) > 5:
            correlation = daily_stats['working_hours'].corr(daily_stats['avg_efficiency'])
            if correlation < -0.3:  # Strong negative correlation indicates fatigue
                return int(daily_stats['working_hours'].quantile(0.7))  # 70th percentile
        
        return 8  # Default assumption: 8 hours before fatigue
    
    def _calculate_consistency(self, driver_rides: pd.DataFrame) -> float:
        """Calculate how consistent the driver's patterns are (0-1 scale)"""
        # Measure consistency in daily start times
        daily_first_ride = driver_rides.groupby('date')['hour'].min()
        start_time_std = daily_first_ride.std()
        
        # Measure consistency in daily ride counts
        daily_rides = driver_rides.groupby('date').size()
        ride_count_cv = daily_rides.std() / daily_rides.mean() if daily_rides.mean() > 0 else 1
        
        # Combine metrics (lower values = more consistent)
        consistency = 1 / (1 + start_time_std + ride_count_cv)
        return min(consistency, 1.0)
    
    def simulate_optimal_week(self, driver_profile: DriverProfile) -> Dict:
        """Simulate optimal weekly schedule to maximize earnings"""
        
        # Get baseline current performance
        current_performance = self._get_current_performance(driver_profile.driver_id)
        
        # Generate optimization scenarios
        scenarios = self._generate_scenarios(driver_profile)
        
        # Evaluate each scenario
        results = {}
        for scenario_name, scenario_schedule in scenarios.items():
            projected_earnings = self._project_earnings(driver_profile, scenario_schedule)
            results[scenario_name] = {
                'schedule': scenario_schedule,
                'projected_weekly_earnings': projected_earnings,
                'improvement': ((projected_earnings - current_performance['weekly_earnings']) / current_performance['weekly_earnings']) * 100,
                'feasibility_score': self._calculate_feasibility(driver_profile, scenario_schedule)
            }
        
        return {
            'current_performance': current_performance,
            'scenarios': results,
            'best_scenario': max(results.keys(), key=lambda x: results[x]['projected_weekly_earnings'] * results[x]['feasibility_score'])
        }
    
    def _get_current_performance(self, driver_id: str) -> Dict:
        """Get driver's current performance baseline"""
        driver_earnings = self.earnings_data[self.earnings_data['earner_id'] == driver_id]
        
        if len(driver_earnings) == 0:
            return {'weekly_earnings': 0, 'weekly_hours': 0, 'weekly_rides': 0}
            
        return {
            'weekly_earnings': driver_earnings['total_net_earnings'].mean() * 7,  # Daily avg * 7
            'weekly_hours': driver_earnings['rides_duration_mins'].mean() * 7 / 60,
            'weekly_rides': driver_earnings['trips_count'].mean() * 7
        }
    
    def _generate_scenarios(self, driver_profile: DriverProfile) -> Dict:
        """Generate different optimization scenarios"""
        base_schedule = {day: driver_profile.preferred_hours[:4] for day in driver_profile.peak_days}
        
        scenarios = {
            'current_pattern': base_schedule,
            
            'early_bird': {
                day: [h-2 for h in driver_profile.preferred_hours[:4] if h-2 >= 0] 
                for day in driver_profile.peak_days
            },
            
            'surge_optimizer': {
                day: [17, 18, 19, 20, 21, 22] if day in ['Friday', 'Saturday'] 
                else driver_profile.preferred_hours[:4]
                for day in driver_profile.peak_days + ['Friday', 'Saturday']
            },
            
            'consistent_grind': {
                day: [9, 10, 11, 16, 17, 18] 
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            },
            
            'weekend_warrior': {
                'Friday': [16, 17, 18, 19, 20, 21, 22],
                'Saturday': [12, 13, 14, 18, 19, 20, 21, 22],
                'Sunday': [12, 13, 14, 17, 18, 19]
            }
        }
        
        return scenarios
    
    def _project_earnings(self, driver_profile: DriverProfile, schedule: Dict) -> float:
        """Project earnings based on schedule and driver profile"""
        total_earnings = 0
        
        for day, hours in schedule.items():
            for hour in hours:
                # Base earnings per hour
                base_earnings = driver_profile.avg_earnings_per_hour
                
                # Apply surge multiplier
                surge_mult = self._get_surge_multiplier(hour)
                surge_bonus = base_earnings * (surge_mult - 1) * driver_profile.surge_responsiveness
                
                # Apply fatigue penalty if working too long
                daily_hours = len(hours)
                if daily_hours > driver_profile.fatigue_threshold:
                    fatigue_penalty = 0.1 * (daily_hours - driver_profile.fatigue_threshold)
                    base_earnings *= (1 - fatigue_penalty)
                
                # Peak day bonus
                if day in driver_profile.peak_days:
                    base_earnings *= 1.1
                
                total_earnings += base_earnings + surge_bonus
                
        return total_earnings
    
    def _get_surge_multiplier(self, hour: int) -> float:
        """Get average surge multiplier for given hour"""
        surge_hour = self.surge_data[self.surge_data['hour'] == hour]
        if len(surge_hour) > 0:
            return surge_hour['surge_multiplier'].mean()
        return 1.0
    
    def _calculate_feasibility(self, driver_profile: DriverProfile, schedule: Dict) -> float:
        """Calculate how feasible this schedule is for the driver (0-1)"""
        # Check consistency with driver's patterns
        total_hours = sum(len(hours) for hours in schedule.values())
        
        # Penalize if too different from their patterns
        pattern_match = len(set(driver_profile.preferred_hours) & 
                          set([h for hours in schedule.values() for h in hours])) / len(driver_profile.preferred_hours)
        
        # Penalize overwork
        overwork_penalty = max(0, (total_hours - driver_profile.fatigue_threshold * len(schedule)) / 10)
        
        # Reward consistency
        consistency_bonus = driver_profile.consistency_score * 0.2
        
        feasibility = pattern_match + consistency_bonus - overwork_penalty
        return max(0, min(1, feasibility))
    
    def visualize_driver_profile(self, driver_profile: DriverProfile):
        """Create comprehensive visualization of driver profile"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Preferred hours heatmap
        hours_data = np.zeros(24)
        for hour in driver_profile.preferred_hours:
            hours_data[hour] = 1
        
        axes[0,0].bar(range(24), hours_data, color='skyblue')
        axes[0,0].set_title('Preferred Working Hours')
        axes[0,0].set_xlabel('Hour of Day')
        axes[0,0].set_ylabel('Activity Level')
        
        # 2. Peak days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_activity = [1 if day in driver_profile.peak_days else 0.3 for day in days]
        
        axes[0,1].bar(days, day_activity, color='lightgreen')
        axes[0,1].set_title('Peak Days Activity')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Key metrics radar chart
        metrics = ['Earnings/Hour', 'Surge Response', 'Consistency', 'Incentive Rate']
        values = [
            min(driver_profile.avg_earnings_per_hour / 20, 1),  # Normalize to 0-1
            abs(driver_profile.surge_responsiveness),
            driver_profile.consistency_score,
            driver_profile.incentive_completion_rate
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        axes[0,2].plot(angles, values, 'o-', linewidth=2, color='purple')
        axes[0,2].fill(angles, values, alpha=0.25, color='purple')
        axes[0,2].set_xticks(angles[:-1])
        axes[0,2].set_xticklabels(metrics)
        axes[0,2].set_title('Driver Profile Radar')
        axes[0,2].set_ylim(0, 1)
        
        # 4. Earnings distribution by hour
        driver_rides = self.rides_data[self.rides_data['driver_id'] == driver_profile.driver_id]
        hourly_earnings = driver_rides.groupby('hour')['earnings_per_hour'].mean()
        
        axes[1,0].plot(hourly_earnings.index, hourly_earnings.values, marker='o', color='orange')
        axes[1,0].set_title('Hourly Earnings Pattern')
        axes[1,0].set_xlabel('Hour of Day')
        axes[1,0].set_ylabel('Avg Earnings per Hour (€)')
        
        # 5. Weekly pattern
        daily_rides = driver_rides.groupby('day_name').size()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_rides = daily_rides.reindex(day_order, fill_value=0)
        
        axes[1,1].bar(daily_rides.index, daily_rides.values, color='coral')
        axes[1,1].set_title('Weekly Ride Distribution')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # 6. Key stats summary
        stats_text = f"""
        Driver ID: {driver_profile.driver_id}
        
        📊 Performance Metrics:
        • Avg Earnings/Hour: €{driver_profile.avg_earnings_per_hour:.2f}
        • Surge Responsiveness: {driver_profile.surge_responsiveness:.2f}
        • Fatigue Threshold: {driver_profile.fatigue_threshold}h
        • Consistency Score: {driver_profile.consistency_score:.2f}
        • Incentive Completion: {driver_profile.incentive_completion_rate:.1%}
        
        🕒 Preferred Hours: {', '.join(map(str, driver_profile.preferred_hours[:5]))}...
        📅 Peak Days: {', '.join(driver_profile.peak_days)}
        📍 Preferred Zones: {len(driver_profile.preferred_zones)} zones
        """
        
        axes[1,2].text(0.05, 0.95, stats_text, transform=axes[1,2].transAxes, 
                      fontsize=10, verticalalignment='top', fontfamily='monospace',
                      bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        axes[1,2].set_xlim(0, 1)
        axes[1,2].set_ylim(0, 1)
        axes[1,2].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def print_optimization_results(self, optimization_results: Dict):
        """Print detailed optimization results"""
        print("🤖 DIGITAL TWIN OPTIMIZATION RESULTS 🤖")
        print("="*60)
        
        current = optimization_results['current_performance']
        print(f"📊 CURRENT PERFORMANCE:")
        print(f"   Weekly Earnings: €{current['weekly_earnings']:.2f}")
        print(f"   Weekly Hours: {current['weekly_hours']:.1f}h")
        print(f"   Weekly Rides: {current['weekly_rides']:.0f}")
        print()
        
        print("🎯 OPTIMIZATION SCENARIOS:")
        print("-"*60)
        
        scenarios = optimization_results['scenarios']
        best_scenario = optimization_results['best_scenario']
        
        for scenario_name, data in scenarios.items():
            marker = "⭐ BEST" if scenario_name == best_scenario else "  "
            improvement = data['improvement']
            feasibility = data['feasibility_score']
            
            print(f"{marker} {scenario_name.upper()}")
            print(f"   Projected Earnings: €{data['projected_weekly_earnings']:.2f}")
            print(f"   Improvement: {improvement:+.1f}%")
            print(f"   Feasibility: {feasibility:.1%}")
            
            # Show schedule
            schedule = data['schedule']
            print("   Schedule:")
            for day, hours in schedule.items():
                if hours:
                    time_ranges = self._format_hours(hours)
                    print(f"     {day}: {time_ranges}")
            print()
        
        # Recommendation
        best = scenarios[best_scenario]
        print("💡 RECOMMENDATION:")
        print(f"Switch to the '{best_scenario}' strategy for €{best['projected_weekly_earnings'] - current['weekly_earnings']:.2f} more per week!")
        
        if best['improvement'] > 10:
            print("🚀 This could significantly boost your earnings!")
        elif best['improvement'] > 0:
            print("✨ A small optimization that adds up over time.")
        else:
            print("🔍 Your current pattern is already quite good!")
    
    def _format_hours(self, hours: List[int]) -> str:
        """Format list of hours into readable time ranges"""
        if not hours:
            return "No rides"
            
        sorted_hours = sorted(hours)
        ranges = []
        start = sorted_hours[0]
        end = start
        
        for i in range(1, len(sorted_hours)):
            if sorted_hours[i] == end + 1:
                end = sorted_hours[i]
            else:
                ranges.append(f"{start}:00-{end+1}:00")
                start = sorted_hours[i]
                end = start
        
        ranges.append(f"{start}:00-{end+1}:00")
        return ", ".join(ranges)


def main():
    """Demo of the Digital Twin Agent"""
    # Initialize the agent
    agent = DigitalTwinAgent()
    
    # Get a driver with substantial data
    driver_counts = agent.rides_data['driver_id'].value_counts()
    top_driver = driver_counts.index[0]  # Most active driver
    
    print(f"🧍‍♂️ Creating Digital Twin for driver: {top_driver}")
    print("="*60)
    
    # Learn driver patterns
    try:
        profile = agent.learn_driver_patterns(top_driver)
        
        # Visualize the profile
        agent.visualize_driver_profile(profile)
        
        # Run optimization
        optimization = agent.simulate_optimal_week(profile)
        
        # Print results
        agent.print_optimization_results(optimization)
        
    except Exception as e:
        print(f"Error analyzing driver {top_driver}: {e}")
        return
    
    print("\n🎯 To analyze a different driver, use:")
    print("   profile = agent.learn_driver_patterns('DRIVER_ID')")
    print("   optimization = agent.simulate_optimal_week(profile)")


if __name__ == "__main__":
    main()