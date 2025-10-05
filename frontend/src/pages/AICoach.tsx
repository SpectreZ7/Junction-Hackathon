import { Card } from "@/components/ui/card";
import { Navigation, RefreshCw, Clock, DollarSign, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";

interface RouteStop {
  sequence: number;
  peak_id?: string;
  source?: string;
  type?: string;
  location: string;
  arrival_time?: string;
  duration_minutes?: number;
  service_time_window: string;
  departure_time: string;
  base_revenue: number;
  weather_adjusted_revenue: number;
  weather_multiplier: number;
  weather_conditions: string;
  estimated_wait_minutes: number;
  travel_to_next_minutes: number;
  reasoning: string;
}

interface RouteSummary {
  total_base_revenue: number;
  total_weather_adjusted_revenue: number;
  weather_bonus_revenue: number;
  total_active_time_hours: number;
  revenue_per_hour: number;
  number_of_stops: number;
  total_distance_miles: number;
  total_wait_time_minutes: number;
  bad_weather_stops: number;
  good_weather_stops: number;
  efficiency_score: number;
  confidence: number;
}

interface RejectedOpportunity {
  peak_id: string;
  reason: string;
  potential_revenue_lost: number;
}

interface OrchestratorResponse {
  optimal_route: RouteStop[];
  rejected_opportunities: RejectedOpportunity[];
  summary: RouteSummary;
  weather_strategy: string;
  execution_strategy: string;
  risk_assessment: string;
  city: string;
  timestamp: string;
}

interface OrchestratorData {
  orchestrator_response: OrchestratorResponse;
}

const RouteOptimizer = () => {
  const [routeData, setRouteData] = useState<OrchestratorData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  const fetchRouteData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get wellbeing score from localStorage
      const wellbeingScore = localStorage.getItem('wellbeingScore');
      const wellbeingValue = wellbeingScore ? parseFloat(wellbeingScore) : 85; // Default to 85 if not found
      
      const response = await fetch('http://127.0.0.1:1003/orchestrate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          city: 'New York',
          driver_id: 'E10156',
          wellbeing_score: wellbeingValue
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: OrchestratorData = await response.json();
      setRouteData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load route data');
      console.error('Route API fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRouteData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-teal-900 to-cyan-900 pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl font-bold text-white">Today's Route</h1>
              {routeData && <p className="text-sm text-emerald-300">{routeData.orchestrator_response.city}</p>}
            </div>
            <button
              onClick={fetchRouteData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 text-white rounded-lg transition-all duration-200 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>
          {lastUpdate && (
            <p className="text-xs text-emerald-400">Updated {lastUpdate}</p>
          )}
        </div>

        {/* Thinking Animation */}
        {loading && (
          <Card className="p-6 bg-emerald-900/30 border-emerald-700/50">
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" style={{ animationDelay: '0s' }}></div>
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
              <p className="text-emerald-400 text-sm animate-pulse">Planning your route...</p>
            </div>
          </Card>
        )}

        {/* Error Display */}
        {error && !loading && (
          <Card className="p-4 bg-red-900/20 border-red-500/50">
            <p className="text-red-400 text-sm">{error}</p>
          </Card>
        )}

        {/* Quick Stats */}
        {!loading && routeData && (
          <>
            <Card className="p-5 bg-gradient-to-br from-emerald-600 to-teal-600 border-emerald-500/50 shadow-lg">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-emerald-100 text-sm">Today's Earnings</p>
                  <p className="text-3xl font-bold text-white">${routeData.orchestrator_response.summary.total_weather_adjusted_revenue}</p>
                </div>
                <div>
                  <p className="text-emerald-100 text-sm">Number of Stops</p>
                  <p className="text-3xl font-bold text-white">{routeData.orchestrator_response.summary.number_of_stops}</p>
                </div>
              </div>
            </Card>

            {/* Route Steps */}
            <div className="space-y-3">
              {routeData.orchestrator_response.optimal_route.map((stop, index) => {
                const isLast = index === routeData.orchestrator_response.optimal_route.length - 1;
                const isBreak = stop.type === 'break';

                return (
                  <div key={stop.peak_id || `break-${index}`} className="relative">
                    <Card className={`p-4 ${isBreak ? 'bg-blue-900/30 border-blue-700/50' : 'bg-teal-900/30 border-teal-700/50'}`}>
                      {/* Step Number */}
                      <div className={`absolute -left-3 -top-3 w-8 h-8 ${isBreak ? 'bg-blue-500' : 'bg-emerald-500'} rounded-full flex items-center justify-center shadow-lg`}>
                        <span className="text-white font-bold">{stop.sequence}</span>
                      </div>

                      <div className="ml-2">
                        {/* Location */}
                        <h3 className="text-xl font-bold text-white mb-2">
                          {isBreak ? '☕ ' : ''}{stop.location}
                        </h3>

                        {isBreak ? (
                          /* Break Info */
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-blue-400" />
                              <div>
                                <p className="text-xs text-slate-400">Break Duration</p>
                                <p className="text-sm font-bold text-blue-400">{stop.duration_minutes} minutes</p>
                              </div>
                            </div>
                            <p className="text-xs text-blue-300 italic">{stop.reasoning}</p>
                          </div>
                        ) : (
                          /* Regular Stop Info */
                          <div className="grid grid-cols-2 gap-3 mb-3">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-emerald-400" />
                              <div>
                                <p className="text-xs text-slate-400">Arrive at</p>
                                <p className="text-sm font-bold text-white">{stop.arrival_time}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <DollarSign className="w-4 h-4 text-emerald-400" />
                              <div>
                                <p className="text-xs text-slate-400">Earn</p>
                                <p className="text-sm font-bold text-emerald-400">${stop.weather_adjusted_revenue}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Travel Time to Next */}
                        {!isLast && !isBreak && (
                          <div className="pt-3 border-t border-teal-700/50">
                            <p className="text-xs text-emerald-300">
                              <Navigation className="w-3 h-3 inline mr-1" />
                              {stop.travel_to_next_minutes} min to next stop
                            </p>
                          </div>
                        )}
                      </div>
                    </Card>

                    {/* Connector */}
                    {!isLast && (
                      <div className="pl-4 py-2">
                        <div className={`w-0.5 h-6 ${isBreak ? 'bg-blue-500/50' : 'bg-emerald-500/50'} ml-0.5`}></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Wellbeing Info */}
            {routeData.orchestrator_response.wellbeing_integration && (
              <Card className="p-4 bg-blue-900/20 border-blue-700/50">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-300">Wellbeing Score</p>
                    <p className="text-lg font-bold text-blue-400">{routeData.orchestrator_response.wellbeing_integration.wellbeing_score}</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-300">Breaks Scheduled</p>
                    <p className="text-lg font-bold text-blue-400">{routeData.orchestrator_response.wellbeing_integration.breaks_added}</p>
                  </div>
                  <p className="text-xs text-blue-300 italic">{routeData.orchestrator_response.wellbeing_integration.break_requirements.recommendation}</p>
                </div>
              </Card>
            )}

            {/* Bottom Summary */}
            <Card className="p-4 bg-emerald-900/20 border-emerald-700/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-400">Total Active Time</p>
                  <p className="text-lg font-bold text-white">{routeData.orchestrator_response.summary.total_active_time_hours.toFixed(1)} hours</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400">Per Hour</p>
                  <p className="text-lg font-bold text-emerald-400">${routeData.orchestrator_response.summary.revenue_per_hour.toFixed(2)}/h</p>
                </div>
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default RouteOptimizer;