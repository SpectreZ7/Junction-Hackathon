#!/usr/bin/env python3
"""
Driver Prioritization Agent

Implements an intelligent driver prioritization system using Experience-Aware Rating (EAR)
and multiple reliability/engagement factors to match the best drivers to ride requests.

Factors considered:
- Driver Rating (R): Quality of service (1-5 stars)
- Acceptance Rate (A): How often they accept ride requests  
- Cancellation Rate (C): Reliability (lower is better)
- Total Completed Trips (T): Experience measure
- Recency/Activeness (L): How active they've been recently
- Complaints/Safety Incidents (S): Negative weight

Uses Bayesian shrinkage to balance new vs experienced drivers fairly.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class DriverPriorityScore:
    """Complete priority scoring for a driver"""
    earner_id: str
    
    # Core metrics
    raw_rating: float
    experience_adjusted_rating: float  # EAR
    experience_boost: float  # E(n)
    
    # Reliability metrics
    acceptance_rate: float
    cancellation_reliability: float  # 1 - cancel_rate
    recent_activeness: float
    safety_score: float
    
    # Final scores
    overall_priority_score: float
    rank: int


class DriverPrioritizationAgent:
    """
    Intelligent driver prioritization using Experience-Aware Rating (EAR)
    and multi-factor reliability assessment.
    """
    
    def __init__(self, data_path: str = "data/uber_mock_data.xlsx"):
        """Initialize with driver data"""
        # Load earner data
        self.drivers_df = pd.read_excel(data_path, sheet_name=0)
        
        # Try to load rides data for more accurate metrics
        try:
            self.rides_df = pd.read_excel(data_path, sheet_name="rides_trips")
            self.has_rides_data = True
        except:
            self.rides_df = None
            self.has_rides_data = False
        
        # Configuration parameters
        self.config = {
            'platform_avg_rating': 4.7,  # Global prior (a)
            'equivalent_prior_trips': 20,  # m - how many trips before rating stabilizes
            'n95_trips': 500,  # Trip count for 95% of max experience credit
            'max_incidents': 10,  # For normalizing safety scores
            'activeness_window_days': 30,  # Look at last 30 days
        }
        
        # Weights for combining factors
        self.weights = {
            'rating': 0.35,
            'acceptance': 0.15,
            'cancellation': 0.15,
            'activeness': 0.15,
            'safety': 0.10,
            'experience_boost': 0.10,
        }
        
        # Enrich driver data with calculated metrics
        self._enrich_driver_data()
    
    def _enrich_driver_data(self):
        """Calculate additional metrics for each driver"""
        np.random.seed(42)  # For reproducible mock data
        
        # Use experience_months to estimate completed trips
        # Assuming avg 100 trips per month for active drivers
        self.drivers_df['completed_trips'] = (
            self.drivers_df['experience_months'] * 
            np.random.uniform(80, 120, len(self.drivers_df))
        ).astype(int)
        
        # Generate realistic acceptance rates (better drivers accept more)
        # Correlate with rating
        rating_normalized = (self.drivers_df['rating'] - 4.2) / 0.8
        self.drivers_df['acceptance_rate'] = np.clip(
            rating_normalized * 0.3 + np.random.uniform(0.6, 0.95, len(self.drivers_df)),
            0.5, 1.0
        )
        
        # Generate cancellation rates (better drivers cancel less)
        self.drivers_df['cancellation_rate'] = np.clip(
            (5.0 - self.drivers_df['rating']) * 0.04 + np.random.uniform(0, 0.08, len(self.drivers_df)),
            0.0, 0.25
        )
        
        # Generate recent activeness based on status
        base_activeness = {
            'online': np.random.uniform(0.7, 1.0),
            'engaged': np.random.uniform(0.7, 1.0),
            'offline': np.random.uniform(0.0, 0.5)
        }
        self.drivers_df['days_active_last30'] = self.drivers_df['status'].apply(
            lambda s: np.random.uniform(*self._activeness_range(s))
        )
        self.drivers_df['activeness_score'] = self.drivers_df['days_active_last30'] / 30
        
        # Generate safety/complaint scores (fewer incidents = better score)
        # Better rated drivers have fewer incidents
        incident_rate = (5.0 - self.drivers_df['rating']) * 0.5
        self.drivers_df['safety_incidents'] = np.random.poisson(
            incident_rate, len(self.drivers_df)
        )
        self.drivers_df['safety_score'] = 1 - (
            self.drivers_df['safety_incidents'] / self.config['max_incidents']
        )
        self.drivers_df['safety_score'] = self.drivers_df['safety_score'].clip(0, 1)
    
    def _activeness_range(self, status: str) -> Tuple[float, float]:
        """Return activeness range based on status"""
        ranges = {
            'online': (20, 30),
            'engaged': (20, 30),
            'offline': (0, 15)
        }
        return ranges.get(status, (10, 20))
    
    def calculate_experience_aware_rating(
        self, 
        driver_rating: float, 
        completed_trips: int
    ) -> float:
        """
        Calculate Experience-Aware Rating (EAR) using Bayesian shrinkage.
        
        Formula: EAR = (m * a + n * r) / (m + n)
        where:
        - r = driver's rating (1-5)
        - n = total completed trips
        - a = platform-wide average rating
        - m = equivalent prior trips (how much weight to give the prior)
        
        This shrinks each driver's rating toward the global average,
        with less shrinkage as they complete more trips.
        """
        a = self.config['platform_avg_rating']
        m = self.config['equivalent_prior_trips']
        n = completed_trips
        r = driver_rating
        
        ear = (m * a + n * r) / (m + n)
        return ear
    
    def calculate_experience_boost(self, completed_trips: int) -> float:
        """
        Calculate experience boost factor E(n).
        
        Formula: E(n) = log(1+n) / log(1 + N95)
        where N95 is the trip count where you want ~95% of max experience credit.
        
        This rewards volume with diminishing returns - a driver with 1000 trips
        isn't twice as good as one with 500 trips.
        """
        n = completed_trips
        n95 = self.config['n95_trips']
        
        if n <= 0:
            return 0.0
        
        experience_boost = np.log(1 + n) / np.log(1 + n95)
        return min(experience_boost, 1.0)  # Cap at 1.0
    
    def calculate_reliability_score(
        self,
        acceptance_rate: float,
        cancellation_rate: float
    ) -> Tuple[float, float]:
        """
        Calculate reliability metrics.
        
        Returns:
        - A: Acceptance reliability (0-1)
        - C: Cancellation reliability (0-1, where 1 = never cancels)
        """
        A = acceptance_rate  # Already 0-1
        C = 1 - cancellation_rate  # Invert so higher is better
        return A, C
    
    def calculate_overall_priority_score(
        self,
        ear: float,
        experience_boost: float,
        acceptance_rate: float,
        cancellation_reliability: float,
        activeness_score: float,
        safety_score: float
    ) -> float:
        """
        Calculate overall priority score by combining all factors with weights.
        
        Score = w₁*EAR + w₂*A + w₃*C + w₄*L + w₅*S + w₆*E(n)
        
        Returns score in range [0, 1]
        """
        # Normalize EAR to 0-1 scale (from 1-5 star scale)
        ear_normalized = (ear - 1) / 4
        
        score = (
            self.weights['rating'] * ear_normalized +
            self.weights['acceptance'] * acceptance_rate +
            self.weights['cancellation'] * cancellation_reliability +
            self.weights['activeness'] * activeness_score +
            self.weights['safety'] * safety_score +
            self.weights['experience_boost'] * experience_boost
        )
        
        return score
    
    def prioritize_all_drivers(self) -> List[DriverPriorityScore]:
        """Calculate priority scores for all drivers and rank them"""
        priority_scores = []
        
        for _, driver in self.drivers_df.iterrows():
            # Calculate EAR
            ear = self.calculate_experience_aware_rating(
                float(driver['rating']),
                int(driver['completed_trips'])
            )
            
            # Calculate experience boost
            exp_boost = self.calculate_experience_boost(int(driver['completed_trips']))
            
            # Get reliability metrics
            A, C = self.calculate_reliability_score(
                float(driver['acceptance_rate']),
                float(driver['cancellation_rate'])
            )
            
            # Calculate overall score
            overall_score = self.calculate_overall_priority_score(
                ear=ear,
                experience_boost=exp_boost,
                acceptance_rate=A,
                cancellation_reliability=C,
                activeness_score=float(driver['activeness_score']),
                safety_score=float(driver['safety_score'])
            )
            
            priority_scores.append(DriverPriorityScore(
                earner_id=str(driver['earner_id']),
                raw_rating=float(driver['rating']),
                experience_adjusted_rating=ear,
                experience_boost=exp_boost,
                acceptance_rate=A,
                cancellation_reliability=C,
                recent_activeness=float(driver['activeness_score']),
                safety_score=float(driver['safety_score']),
                overall_priority_score=overall_score,
                rank=0  # Will be assigned after sorting
            ))
        
        # Sort by overall score (descending) and assign ranks
        priority_scores.sort(key=lambda x: x.overall_priority_score, reverse=True)
        for rank, score in enumerate(priority_scores, 1):
            score.rank = rank
        
        return priority_scores
    
    def get_top_drivers(self, n: int = 10) -> List[DriverPriorityScore]:
        """Get top N prioritized drivers"""
        all_scores = self.prioritize_all_drivers()
        return all_scores[:n]
    
    def get_driver_priority(self, earner_id: str) -> Optional[DriverPriorityScore]:
        """Get priority score for a specific driver"""
        all_scores = self.prioritize_all_drivers()
        for score in all_scores:
            if score.earner_id == earner_id:
                return score
        return None
    
    def print_priority_report(self, scores: List[DriverPriorityScore]):
        """Print detailed priority report"""
        print("=" * 100)
        print(" 🎯 DRIVER PRIORITIZATION REPORT - Experience-Aware Rating (EAR) System")
        print("=" * 100)
        print()
        
        print(f"📊 System Configuration:")
        print(f"   Platform Average Rating: {self.config['platform_avg_rating']:.2f}")
        print(f"   Equivalent Prior Trips: {self.config['equivalent_prior_trips']}")
        print(f"   N95 Experience Threshold: {self.config['n95_trips']} trips")
        print()
        
        print(f"⚖️  Factor Weights:")
        for factor, weight in self.weights.items():
            print(f"   {factor.capitalize():.<30} {weight:.1%}")
        print()
        
        print("=" * 100)
        print(f"{'Rank':<6} {'Driver ID':<12} {'Raw★':<7} {'EAR★':<7} {'Exp↑':<7} "
              f"{'Accept':<8} {'!Cancel':<8} {'Active':<8} {'Safety':<8} {'PRIORITY':<10}")
        print("=" * 100)
        
        for score in scores:
            print(f"{score.rank:<6} "
                  f"{score.earner_id:<12} "
                  f"{score.raw_rating:<7.2f} "
                  f"{score.experience_adjusted_rating:<7.2f} "
                  f"{score.experience_boost:<7.2%} "
                  f"{score.acceptance_rate:<8.1%} "
                  f"{score.cancellation_reliability:<8.1%} "
                  f"{score.recent_activeness:<8.1%} "
                  f"{score.safety_score:<8.1%} "
                  f"{score.overall_priority_score:<10.4f}")
        
        print("=" * 100)
        print()
        
        # Insights
        top_driver = scores[0]
        print(f"🏆 Top Driver: {top_driver.earner_id}")
        print(f"   Priority Score: {top_driver.overall_priority_score:.4f}")
        print(f"   EAR (Experience-Adjusted Rating): {top_driver.experience_adjusted_rating:.2f}★")
        print(f"   Experience Boost: {top_driver.experience_boost:.1%}")
        print(f"   Key Strength: ", end="")
        
        # Identify key strength
        strengths = {
            'Rating': top_driver.raw_rating / 5,
            'Acceptance': top_driver.acceptance_rate,
            'Reliability': top_driver.cancellation_reliability,
            'Activeness': top_driver.recent_activeness,
            'Safety': top_driver.safety_score,
            'Experience': top_driver.experience_boost
        }
        best_strength = max(strengths.keys(), key=lambda k: strengths[k])
        print(f"{best_strength} ({strengths[best_strength]:.1%})")
        print()
    
    def visualize_priority_factors(self, top_n: int = 20):
        """Create comprehensive visualization of priority factors"""
        scores = self.get_top_drivers(top_n)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('🎯 Driver Prioritization Analysis - Top 20 Drivers', 
                     fontsize=16, fontweight='bold')
        
        # Prepare data for plotting
        driver_ids = [s.earner_id[-4:] for s in scores]  # Last 4 digits for readability
        
        # 1. Overall Priority Scores
        priority_scores = [s.overall_priority_score for s in scores]
        cmap = plt.colormaps.get_cmap('RdYlGn')
        colors = cmap(np.linspace(0.3, 0.9, len(priority_scores)))
        
        axes[0, 0].barh(driver_ids, priority_scores, color=colors)
        axes[0, 0].set_xlabel('Priority Score')
        axes[0, 0].set_title('Overall Priority Ranking')
        axes[0, 0].invert_yaxis()
        
        # 2. Raw Rating vs EAR
        raw_ratings = [s.raw_rating for s in scores]
        ear_ratings = [s.experience_adjusted_rating for s in scores]
        
        x = np.arange(len(driver_ids))
        width = 0.35
        axes[0, 1].bar(x - width/2, raw_ratings, width, label='Raw Rating', alpha=0.8)
        axes[0, 1].bar(x + width/2, ear_ratings, width, label='EAR (Adjusted)', alpha=0.8)
        axes[0, 1].set_ylabel('Rating (Stars)')
        axes[0, 1].set_title('Raw Rating vs Experience-Adjusted Rating')
        axes[0, 1].set_xticks(x[::2])
        axes[0, 1].set_xticklabels(driver_ids[::2], rotation=45)
        axes[0, 1].legend()
        axes[0, 1].set_ylim(4, 5)
        
        # 3. Experience Boost Distribution
        exp_boosts = [s.experience_boost for s in scores]
        axes[0, 2].scatter(range(len(exp_boosts)), exp_boosts, 
                          c=priority_scores, cmap='viridis', s=100, alpha=0.6)
        axes[0, 2].set_xlabel('Driver Rank')
        axes[0, 2].set_ylabel('Experience Boost E(n)')
        axes[0, 2].set_title('Experience Boost Factor')
        axes[0, 2].axhline(y=0.95, color='r', linestyle='--', alpha=0.3, 
                          label='95% threshold')
        axes[0, 2].legend()
        
        # 4. Reliability Metrics Heatmap
        reliability_data = np.array([
            [s.acceptance_rate for s in scores],
            [s.cancellation_reliability for s in scores],
            [s.recent_activeness for s in scores],
            [s.safety_score for s in scores]
        ])
        
        im = axes[1, 0].imshow(reliability_data, aspect='auto', cmap='RdYlGn', 
                               vmin=0, vmax=1)
        axes[1, 0].set_yticks(range(4))
        axes[1, 0].set_yticklabels(['Acceptance', 'Reliability', 'Activeness', 'Safety'])
        axes[1, 0].set_xticks(range(0, len(driver_ids), 2))
        axes[1, 0].set_xticklabels(driver_ids[::2], rotation=45)
        axes[1, 0].set_title('Reliability Metrics Heatmap')
        plt.colorbar(im, ax=axes[1, 0])
        
        # 5. Factor Contribution Breakdown (for top driver)
        top_score = scores[0]
        ear_norm = (top_score.experience_adjusted_rating - 1) / 4
        contributions = {
            'EAR': self.weights['rating'] * ear_norm,
            'Acceptance': self.weights['acceptance'] * top_score.acceptance_rate,
            'Reliability': self.weights['cancellation'] * top_score.cancellation_reliability,
            'Activeness': self.weights['activeness'] * top_score.recent_activeness,
            'Safety': self.weights['safety'] * top_score.safety_score,
            'Experience': self.weights['experience_boost'] * top_score.experience_boost
        }
        
        axes[1, 1].pie(contributions.values(), labels=contributions.keys(), 
                      autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title(f'Priority Score Breakdown\n(Top Driver: {top_score.earner_id})')
        
        # 6. Score Distribution
        all_scores = self.prioritize_all_drivers()
        all_priority_scores = [s.overall_priority_score for s in all_scores]
        
        axes[1, 2].hist(all_priority_scores, bins=30, color='skyblue', edgecolor='black')
        axes[1, 2].axvline(x=scores[-1].overall_priority_score, color='r', 
                          linestyle='--', label=f'Top {top_n} cutoff')
        axes[1, 2].set_xlabel('Priority Score')
        axes[1, 2].set_ylabel('Number of Drivers')
        axes[1, 2].set_title('Priority Score Distribution (All Drivers)')
        axes[1, 2].legend()
        
        plt.tight_layout()
        plt.show()
    
    def explain_algorithm(self):
        """Print detailed explanation of the algorithm"""
        print("=" * 100)
        print(" 📚 EXPERIENCE-AWARE RATING (EAR) ALGORITHM EXPLANATION")
        print("=" * 100)
        print()
        
        print("🎯 OBJECTIVE:")
        print("   Fairly prioritize drivers considering both quality AND experience,")
        print("   while accounting for reliability, activeness, and safety.")
        print()
        
        print("📊 CORE FORMULA - Experience-Aware Rating (EAR):")
        print()
        print("   EAR = (m × a + n × r) / (m + n)")
        print()
        print("   where:")
        print(f"   • r = driver's raw rating (1-5 stars)")
        print(f"   • n = total completed trips")
        print(f"   • a = platform-wide average rating ({self.config['platform_avg_rating']})")
        print(f"   • m = equivalent prior trips ({self.config['equivalent_prior_trips']})")
        print()
        print("   This uses Bayesian shrinkage to:")
        print("   - Pull new drivers' ratings toward the global average (prevents lucky/unlucky starts)")
        print("   - Give more weight to experienced drivers' actual ratings")
        print()
        
        print("📈 EXPERIENCE BOOST - E(n):")
        print()
        print("   E(n) = log(1+n) / log(1 + N95)")
        print()
        print(f"   where N95 = {self.config['n95_trips']} trips (95% of max experience credit)")
        print()
        print("   This rewards volume with diminishing returns:")
        print("   - 50 trips  → ~35% experience credit")
        print("   - 100 trips → ~48% experience credit")
        print("   - 500 trips → ~95% experience credit")
        print("   - 1000 trips → ~99% experience credit")
        print()
        
        print("⚖️  RELIABILITY & ENGAGEMENT FACTORS:")
        print()
        print("   A = Acceptance Rate (0-1)")
        print("      How often the driver accepts ride requests")
        print()
        print("   C = 1 - Cancellation Rate (0-1)")
        print("      Reliability measure (higher = more reliable)")
        print()
        print("   L = days_active_last30 / 30 (0-1)")
        print("      Recent activeness in last 30 days")
        print()
        print("   S = 1 - incidents/Smax (0-1)")
        print("      Safety score (normalized complaints/incidents)")
        print()
        
        print("🎲 FINAL PRIORITY SCORE:")
        print()
        print("   Priority = Σ(weight_i × factor_i)")
        print()
        print("   Current weights:")
        for factor, weight in self.weights.items():
            print(f"   • {factor.capitalize():<20} {weight:.1%}")
        print()
        
        print("💡 WHY THIS WORKS:")
        print("   ✅ Fair to new drivers (Bayesian shrinkage prevents rating volatility)")
        print("   ✅ Rewards experience (but with diminishing returns)")
        print("   ✅ Considers reliability (acceptance & cancellation)")
        print("   ✅ Encourages activeness (recent activity matters)")
        print("   ✅ Prioritizes safety (penalizes incidents)")
        print("   ✅ Balanced (multiple factors prevent gaming the system)")
        print()
        print("=" * 100)


def main():
    """Demo the driver prioritization system"""
    print("\n🚀 Initializing Driver Prioritization Agent...\n")
    
    agent = DriverPrioritizationAgent()
    
    # Show algorithm explanation
    agent.explain_algorithm()
    
    print("\n" + "="*100)
    input("Press Enter to see Top 20 drivers...")
    print()
    
    # Get top 20 drivers
    top_drivers = agent.get_top_drivers(n=20)
    
    # Print report
    agent.print_priority_report(top_drivers)
    
    # Visualize
    print("📊 Generating visualizations...")
    agent.visualize_priority_factors(top_n=20)
    
    # Example: Check specific driver
    print("\n" + "="*100)
    print("🔍 INDIVIDUAL DRIVER LOOKUP EXAMPLE")
    print("="*100)
    
    specific_driver = top_drivers[5].earner_id  # 6th best driver
    driver_score = agent.get_driver_priority(specific_driver)
    
    if driver_score:
        print(f"\nDriver: {driver_score.earner_id}")
        print(f"Rank: #{driver_score.rank} out of {len(agent.drivers_df)}")
        print(f"Priority Score: {driver_score.overall_priority_score:.4f}")
        print(f"\nBreakdown:")
        print(f"  Raw Rating: {driver_score.raw_rating:.2f}★")
        print(f"  Experience-Adjusted Rating (EAR): {driver_score.experience_adjusted_rating:.2f}★")
        print(f"  Experience Boost: {driver_score.experience_boost:.1%}")
        print(f"  Acceptance Rate: {driver_score.acceptance_rate:.1%}")
        print(f"  Cancellation Reliability: {driver_score.cancellation_reliability:.1%}")
        print(f"  Recent Activeness: {driver_score.recent_activeness:.1%}")
        print(f"  Safety Score: {driver_score.safety_score:.1%}")
    
    print("\n✅ Driver Prioritization System Ready!")
    print("   This system can be integrated into the ride dispatch flow")
    print("   to match the best available drivers to incoming requests.")


if __name__ == "__main__":
    main()

