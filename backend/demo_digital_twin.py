#!/usr/bin/env python3
"""
🚗🤖 UBER DRIVER DIGITAL TWIN DEMO 🤖🚗

This demo shows how to use the AI "shadow driver" system to:
1. Analyze current driver patterns
2. Learn behavioral preferences 
3. Simulate optimal scheduling strategies
4. Provide actionable recommendations

The Digital Twin learns from historical data to understand:
- When they usually drive
- Which zones they prefer
- How they respond to surge pricing
- Their fatigue and efficiency patterns
- Incentive completion behavior

Then it runs "what-if" scenarios to optimize their earnings!
"""

import sys
import os
sys.path.append('agents')

from rides_analysis_agent import analyze_driver, get_driver_summary, create_digital_twin, data
from digital_twin_agent import DigitalTwinAgent

def demo_driver_analysis(driver_id: str = None):
    """Run complete analysis on a driver"""
    
    if driver_id is None:
        # Pick a driver with substantial data
        driver_counts = data['driver_id'].value_counts()
        driver_id = driver_counts.index[0]  # Most active driver
    
    print("🚗" * 30)
    print("UBER DRIVER OPTIMIZATION SYSTEM")
    print("🚗" * 30)
    print()
    
    # Step 1: Basic Analysis
    print("📊 STEP 1: BASIC PATTERN ANALYSIS")
    print("-" * 50)
    analyze_driver(driver_id)
    
    print("\n" + "🤖" * 30)
    print("AI DIGITAL TWIN ANALYSIS")
    print("🤖" * 30)
    print()
    
    # Step 2: Digital Twin Analysis
    print("🧠 STEP 2: LEARNING DRIVER BEHAVIOR...")
    print("-" * 50)
    
    try:
        agent = DigitalTwinAgent()
        profile = agent.learn_driver_patterns(driver_id)
        
        print("✅ Driver behavioral profile learned!")
        print(f"   • Preferred hours: {', '.join(map(str, profile.preferred_hours[:5]))}")
        print(f"   • Peak days: {', '.join(profile.peak_days)}")
        print(f"   • Avg earnings/hour: €{profile.avg_earnings_per_hour:.2f}")
        print(f"   • Surge responsiveness: {profile.surge_responsiveness:.2f}")
        print(f"   • Fatigue threshold: {profile.fatigue_threshold}h")
        print(f"   • Consistency score: {profile.consistency_score:.2f}")
        
        print("\n🎯 STEP 3: OPTIMIZING WEEKLY SCHEDULE...")
        print("-" * 50)
        
        optimization = agent.simulate_optimal_week(profile)
        
        # Show key recommendations
        best_scenario = optimization['best_scenario']
        best_data = optimization['scenarios'][best_scenario]
        current_earnings = optimization['current_performance']['weekly_earnings']
        
        print("💰 KEY INSIGHTS:")
        print(f"   Current weekly earnings: €{current_earnings:.2f}")
        print(f"   Optimized earnings: €{best_data['projected_weekly_earnings']:.2f}")
        print(f"   Potential increase: €{best_data['projected_weekly_earnings'] - current_earnings:.2f} (+{best_data['improvement']:.1f}%)")
        print(f"   Best strategy: {best_scenario}")
        
        print("\n📈 STEP 4: DETAILED RECOMMENDATIONS")
        print("-" * 50)
        agent.print_optimization_results(optimization)
        
        # Visualizations
        print("\n📊 STEP 5: GENERATING VISUALIZATIONS...")
        print("-" * 50)
        agent.visualize_driver_profile(profile)
        
        return profile, optimization
        
    except Exception as e:
        print(f"❌ Error in Digital Twin analysis: {e}")
        return None, None

def interactive_demo():
    """Interactive demo where user can select drivers"""
    print("🎮 INTERACTIVE DRIVER OPTIMIZATION")
    print("=" * 50)
    
    # Show available drivers
    get_driver_summary()
    
    print("\nSelect a driver to analyze:")
    print("1. Most active driver (recommended)")
    print("2. Enter specific driver ID")
    print("3. Random driver")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    driver_counts = data['driver_id'].value_counts()
    
    if choice == "1":
        selected_driver = driver_counts.index[0]
    elif choice == "2":
        selected_driver = input("Enter driver ID: ").strip()
        if selected_driver not in data['driver_id'].values:
            print(f"❌ Driver {selected_driver} not found!")
            return
    elif choice == "3":
        import random
        selected_driver = random.choice(data['driver_id'].unique())
    else:
        print("Invalid choice, using most active driver")
        selected_driver = driver_counts.index[0]
    
    print(f"\n🎯 Analyzing driver: {selected_driver}")
    print("=" * 50)
    
    # Run analysis
    profile, optimization = demo_driver_analysis(selected_driver)
    
    if profile and optimization:
        print("\n✨ Analysis complete! Key takeaways:")
        best_scenario = optimization['best_scenario'] 
        improvement = optimization['scenarios'][best_scenario]['improvement']
        
        if improvement > 50:
            print("🚀 MAJOR optimization opportunity found!")
        elif improvement > 20:
            print("💡 Good optimization potential identified!")
        elif improvement > 0:
            print("✨ Minor but valuable optimizations available!")
        else:
            print("👍 Driver is already following optimal patterns!")

def compare_drivers():
    """Compare multiple drivers to show different patterns"""
    print("⚖️  DRIVER COMPARISON ANALYSIS")
    print("=" * 50)
    
    # Get top 3 most active drivers
    top_drivers = data['driver_id'].value_counts().head(3).index.tolist()
    
    agent = DigitalTwinAgent()
    profiles = []
    
    print("Comparing top 3 most active drivers...")
    print()
    
    for i, driver_id in enumerate(top_drivers, 1):
        try:
            print(f"🔍 Analyzing Driver #{i}: {driver_id}")
            profile = agent.learn_driver_patterns(driver_id)
            optimization = agent.simulate_optimal_week(profile)
            profiles.append((driver_id, profile, optimization))
            
            best_improvement = optimization['scenarios'][optimization['best_scenario']]['improvement']
            print(f"   Best potential improvement: +{best_improvement:.1f}%")
            print(f"   Consistency score: {profile.consistency_score:.2f}")
            print(f"   Avg earnings/hour: €{profile.avg_earnings_per_hour:.2f}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error analyzing {driver_id}: {e}")
            print()
    
    # Summary comparison
    if len(profiles) >= 2:
        print("📊 COMPARISON SUMMARY:")
        print("-" * 30)
        for driver_id, profile, optimization in profiles:
            best_improvement = optimization['scenarios'][optimization['best_scenario']]['improvement']
            print(f"{driver_id}: {best_improvement:+.1f}% potential | €{profile.avg_earnings_per_hour:.2f}/h | Consistency: {profile.consistency_score:.2f}")

def main():
    """Main demo function"""
    print("🚗🤖 UBER DRIVER DIGITAL TWIN SYSTEM 🤖🚗")
    print("=" * 60)
    print()
    print("This system creates AI 'shadow drivers' that learn from")
    print("historical data to optimize driver schedules and earnings!")
    print()
    print("Choose a demo mode:")
    print("1. 🎯 Full analysis of most active driver")
    print("2. 🎮 Interactive driver selection")
    print("3. ⚖️  Compare multiple drivers")
    print("4. 📚 Technical documentation")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        demo_driver_analysis()
    elif choice == "2":
        interactive_demo()
    elif choice == "3":
        compare_drivers()
    elif choice == "4":
        print(__doc__)
    else:
        print("Invalid choice, running default demo...")
        demo_driver_analysis()

if __name__ == "__main__":
    main()