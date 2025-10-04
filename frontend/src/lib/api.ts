// API Service for Uber Driver AI Companion App
// Connects frontend to the FastAPI backend

const API_BASE_URL = 'http://localhost:8000/api/v1';

interface DriverStatus {
  is_online: boolean;
  earnings_today: number;
  hours_worked: number;
  wellbeing_score: number;
}

interface AIRecommendation {
  type: string;
  title: string;
  message: string;
  projected_earnings?: number;
  improvement?: number;
  peak_time?: string;
  expected_arrivals?: number;
  score?: number;
  status?: string;
}

interface QuickStats {
  rides_today: number;
  rating: number;
  acceptance_rate: number;
  avg_per_hour: number;
}

interface DashboardData {
  driver_id: string;
  status: DriverStatus;
  recommendations: AIRecommendation[];
  quick_stats: QuickStats;
  timestamp: string;
}

interface DigitalTwinProfile {
  preferred_hours: number[];
  peak_days: string[];
  avg_earnings_per_hour: number;
  surge_responsiveness: number;
  fatigue_threshold: number;
  consistency_score: number;
  total_weekly_hours: number;
  preferred_zones: string[];
}

interface OptimizationScenario {
  name: string;
  display_name: string;
  projected_earnings: number;
  improvement: number;
  feasibility: number;
  description: string;
  schedule: Record<string, string>;
  weekly_hours: number;
  is_recommended: boolean;
  confidence: string;
  earnings_breakdown: {
    base_fare: number;
    surge_multiplier: number;
  };
}

interface DriverListItem {
  driver_id: string;
  rides: number;
  status: string;
}

interface DriversListResponse {
  total_drivers: number;
  top_drivers: DriverListItem[];
  sample_ids: string[];
}

interface DriverComparison {
  driver_id: string;
  avg_earnings_per_hour: number;
  surge_response: number;
  consistency: number;
  best_strategy: string;
  current_weekly: number;
  optimized_weekly: number;
}

interface DriverComparisonResponse {
  comparison_date: string;
  drivers: DriverComparison[];
  insights: string[];
}

interface EnhancedDigitalTwinProfile extends DigitalTwinProfile {
  ride_statistics: {
    total_rides: number;
    avg_ride_duration: number;
    busiest_hour: string;
    earnings_per_minute_all: number;
    earnings_per_minute_long: number;
    earnings_per_minute_short: number;
  };
  weekly_breakdown: Record<string, number>;
}

interface WellbeingCheckIn {
  driver_id: string;
  sleep_hours: number;
  fatigue_level: number; // 1-5
  stress_level: number;   // 1-5
  body_discomfort: number; // 1-5
  mood: number; // 1-5
}

interface AirportData {
  airport_code: string;
  airport_name: string;
  city: string;
  peak_intensity: number;
  expected_wait_time: number;
  potential_earnings_per_hour: number;
  recommendation_priority: number;
  next_peak_time: string;
  flight_arrivals_next_hour: number;
}

class UberDriverAPI {
  private baseURL = API_BASE_URL;

  // Helper method for making API calls
  private async fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Dashboard APIs
  async getDashboardData(driverId: string): Promise<DashboardData> {
    return this.fetchAPI<DashboardData>(`/dashboard/${driverId}`);
  }

  // Digital Twin APIs
  async getDigitalTwinProfile(driverId: string): Promise<{
    driver_id: string;
    profile: EnhancedDigitalTwinProfile;
    learning_status: string;
    data_quality: string;
    confidence_score: number;
    last_updated: string;
  }> {
    return this.fetchAPI(`/digital-twin/profile/${driverId}`);
  }

  async optimizeSchedule(driverId: string): Promise<{
    driver_id: string;
    current_performance: {
      weekly_earnings: number;
      weekly_hours: number;
      weekly_rides: number;
      avg_earnings_per_hour: number;
      efficiency_score: number;
    };
    behavioral_profile: {
      preferred_hours: number[];
      peak_days: string[];
      avg_earnings_per_hour: number;
      surge_responsiveness: number;
      fatigue_threshold: number;
      consistency_score: number;
    };
    scenarios: OptimizationScenario[];
    best_scenario: string;
    potential_increase: number;
    key_insights: string[];
    analysis_date: string;
    confidence_level: string;
    data_points_analyzed: number;
  }> {
    return this.fetchAPI(`/digital-twin/optimize`, {
      method: 'POST',
      body: JSON.stringify({ driver_id: driverId }),
    });
  }

  async getAvailableDrivers(): Promise<DriversListResponse> {
    return this.fetchAPI('/digital-twin/drivers');
  }

  async compareDrivers(driverIds: string[]): Promise<DriverComparisonResponse> {
    return this.fetchAPI('/digital-twin/compare', {
      method: 'POST',
      body: JSON.stringify(driverIds),
    });
  }

  // Airport Intelligence APIs
  async getAirportDemand(city: string): Promise<{
    city: string;
    airports: AirportData[];
    last_updated: string;
    data_source: string;
  }> {
    return this.fetchAPI(`/airport/live-demand/${city}`);
  }

  async getSupportedCities(): Promise<{
    cities: Array<{
      name: string;
      airports: string[];
    }>;
  }> {
    return this.fetchAPI('/airport/cities');
  }

  // Wellbeing APIs
  async submitWellbeingCheckIn(checkIn: WellbeingCheckIn): Promise<{
    driver_id: string;
    wellbeing_score: number;
    risk_band: string;
    status: string;
    suggestions: string[];
    timestamp: string;
    should_take_break: boolean;
    can_drive_safely: boolean;
  }> {
    return this.fetchAPI('/wellbeing/check-in', {
      method: 'POST',
      body: JSON.stringify(checkIn),
    });
  }

  async getWellbeingStatus(driverId: string): Promise<{
    driver_id: string;
    current_score: number;
    risk_band: string;
    last_checkin: string;
    trend: string;
    recommendations: string[];
    next_checkin_due: string;
  }> {
    return this.fetchAPI(`/wellbeing/status/${driverId}`);
  }

  // Performance Analytics APIs
  async getPerformanceAnalytics(driverId: string): Promise<{
    driver_id: string;
    priority_score: number;
    performance_metrics: {
      total_rides: number;
      total_earnings: number;
      avg_earnings_per_ride: number;
      weekly_rides: number;
      weekly_earnings: number;
    };
    ratings: {
      current_rating: number;
      rating_trend: string;
      acceptance_rate: number;
      cancellation_rate: number;
    };
    efficiency: {
      rides_per_hour: number;
      earnings_per_hour: number;
      efficiency_score: number;
    };
    analysis_date: string;
  }> {
    return this.fetchAPI(`/analytics/performance/${driverId}`);
  }

  // Driver Management APIs
  async getAllDrivers(): Promise<{
    drivers: Array<{
      driver_id: string;
      total_rides: number;
      status: string;
    }>;
    total_count: number;
  }> {
    return this.fetchAPI('/drivers');
  }

  // Health Check APIs
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    version: string;
    services: Record<string, string>;
  }> {
    return this.fetchAPI('/health', { method: 'GET' });
  }

  async getAPIStatus(): Promise<{
    api_version: string;
    status: string;
    endpoints: Record<string, string>;
    documentation: Record<string, string>;
  }> {
    return this.fetchAPI('/status');
  }
}

// Export a singleton instance
export const uberDriverAPI = new UberDriverAPI();

// Export types for use in components
export type {
  DashboardData,
  DriverStatus,
  AIRecommendation,
  QuickStats,
  DigitalTwinProfile,
  EnhancedDigitalTwinProfile,
  OptimizationScenario,
  WellbeingCheckIn,
  AirportData,
  DriverListItem,
  DriversListResponse,
  DriverComparison,
  DriverComparisonResponse,
};