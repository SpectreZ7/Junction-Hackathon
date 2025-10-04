import { Card } from "@/components/ui/card";
import { Navigation, RefreshCw, MapPin, Clock, DollarSign, TrendingUp, CloudRain, Sun, AlertTriangle, Route } from "lucide-react";
import { useState, useEffect } from "react";

interface RouteStop {
  sequence: number;
  peak_id: string;
  source: string;
  location: string;
  arrival_time: string;
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

interface RejectedOpportunity {
  peak_id: string;
  reason: string;
  potential_revenue_lost: number;
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
      
      const response = await fetch('http://127.0.0.1:1002/orchestrate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city: 'New York' })
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

  const getWeatherIcon = (conditions: string) => {
    if (conditions.toLowerCase().includes('rain')) return CloudRain;
    if (conditions.toLowerCase().includes('clear') || conditions.toLowerCase().includes('sunny')) return Sun;
    return CloudRain;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-teal-900 to-cyan-900 pb-24">
      <div className="max-w-2xl mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Navigation className="w-8 h-8 text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Smart Route Optimizer</h1>
                <p className="text-sm text-emerald-300">AI-powered revenue maximization</p>
              </div>
            </div>
            <button
              onClick={fetchRouteData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 text-white rounded-lg transition-all duration-200 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Generate Route</span>
            </button>
          </div>
          {lastUpdate && (
            <p className="text-xs text-emerald-400">Last generated: {lastUpdate}</p>
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
              <p className="text-emerald-400 text-sm animate-pulse">Optimizing your route...</p>
            </div>
          </Card>
        )}

        {/* Error Display */}
        {error && !loading && (
          <Card className="p-4 bg-red-900/20 border-red-500/50">
            <p className="text-red-400 text-sm">{error}</p>
          </Card>
        )}

        {/* Route Summary Card */}
        {!loading && routeData && (
          <>
            <Card className="p-5 bg-gradient-to-br from-emerald-600 to-teal-600 border-emerald-500/50 shadow-lg shadow-emerald-500/20">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
                <h3 className="text-xl font-bold text-white">Revenue Forecast</h3>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-emerald-100 text-sm">Total Revenue</p>
                  <p className="text-3xl font-bold text-white">${routeData.orchestrator_response.summary.total_weather_adjusted_revenue}</p>
                </div>
                <div>
                  <p className="text-emerald-100 text-sm">Per Hour</p>
                  <p className="text-3xl font-bold text-white">${routeData.orchestrator_response.summary.revenue_per_hour.toFixed(2)}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-3 border-t border-emerald-400/30">
                <div className="text-center">
                  <p className="text-emerald-100 text-xs">Stops</p>
                  <p className="text-xl font-bold text-white">{routeData.orchestrator_response.summary.number_of_stops}</p>
                </div>
                <div className="text-center">
                  <p className="text-emerald-100 text-xs">Total Time</p>
                  <p className="text-xl font-bold text-white">{routeData.orchestrator_response.summary.total_active_time_hours.toFixed(1)}h</p>
                </div>
                <div className="text-center">
                  <p className="text-emerald-100 text-xs">Distance</p>
                  <p className="text-xl font-bold text-white">{routeData.orchestrator_response.summary.total_distance_miles.toFixed(1)}mi</p>
                </div>
              </div>
            </Card>

            {/* Optimal Route */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Route className="w-5 h-5 text-emerald-400" />
                <h2 className="text-xl font-bold text-white">Your Optimized Route</h2>
              </div>

              {routeData.orchestrator_response.optimal_route.map((stop, index) => {
                const WeatherIcon = getWeatherIcon(stop.weather_conditions);
                const isLast = index === routeData.orchestrator_response.optimal_route.length - 1;

                return (
                  <div key={stop.peak_id} className="relative">
                    <Card className="p-4 bg-teal-900/30 border-teal-700/50 backdrop-blur-sm">
                      {/* Stop Number Badge */}
                      <div className="absolute -left-3 -top-3 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                        <span className="text-white font-bold text-sm">{stop.sequence}</span>
                      </div>

                      <div className="ml-3">
                        {/* Location & Time */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-white mb-1">{stop.location}</h3>
                            <div className="flex items-center gap-2 text-emerald-300 text-sm">
                              <Clock className="w-4 h-4" />
                              <span>Arrive: {stop.arrival_time} • Service: {stop.service_time_window}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold text-emerald-400">${stop.weather_adjusted_revenue}</p>
                          </div>
                        </div>

                        {/* Weather & Details */}
                        <div className="grid grid-cols-3 gap-3 mb-3">
                          <div className="flex items-center gap-2">
                            <WeatherIcon className="w-4 h-4 text-cyan-400" />
                            <div>
                              <p className="text-xs text-slate-400">Weather</p>
                              <p className="text-xs font-semibold text-white">{stop.weather_conditions.split(',')[0]}</p>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Wait Time</p>
                            <p className="text-sm font-semibold text-white">{stop.estimated_wait_minutes} min</p>
                          </div>
                          {!isLast && (
                            <div>
                              <p className="text-xs text-slate-400">Next Stop</p>
                              <p className="text-sm font-semibold text-white">{stop.travel_to_next_minutes} min</p>
                            </div>
                          )}
                        </div>

                        {/* Reasoning */}
                        <div className="p-2 bg-teal-800/30 rounded-lg">
                          <p className="text-xs text-emerald-200">{stop.reasoning}</p>
                        </div>
                      </div>
                    </Card>

                    {/* Connector Line */}
                    {!isLast && (
                      <div className="flex items-center gap-2 py-2 pl-4">
                        <div className="w-0.5 h-8 bg-emerald-500/50"></div>
                        <div className="flex items-center gap-2 text-emerald-400 text-xs">
                          <Navigation className="w-3 h-3" />
                          <span>{stop.travel_to_next_minutes} min drive</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Strategy Insights */}
            <Card className="p-4 bg-cyan-900/20 border-cyan-700/50">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                Strategy Insights
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-cyan-300 font-semibold mb-1">Weather Strategy</p>
                  <p className="text-sm text-white">{routeData.orchestrator_response.weather_strategy}</p>
                </div>
                
                <div>
                  <p className="text-xs text-cyan-300 font-semibold mb-1">Execution Plan</p>
                  <p className="text-sm text-white">{routeData.orchestrator_response.execution_strategy}</p>
                </div>

                {routeData.orchestrator_response.risk_assessment && 
                 routeData.orchestrator_response.risk_assessment !== "No significant risks identified due to good weather conditions throughout the route." && (
                  <div className="p-3 bg-yellow-900/20 border border-yellow-700/50 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                      <div>
                        <p className="text-xs text-yellow-300 font-semibold mb-1">Risk Assessment</p>
                        <p className="text-sm text-yellow-100">{routeData.orchestrator_response.risk_assessment}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            {/* Rejected Opportunities */}
            {routeData.orchestrator_response.rejected_opportunities.length > 0 && (
              <Card className="p-4 bg-slate-800/30 border-slate-700/50">
                <h3 className="text-sm font-bold text-slate-300 mb-3">Opportunities Skipped</h3>
                <div className="space-y-2">
                  {routeData.orchestrator_response.rejected_opportunities.slice(0, 5).map((rejected, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">{rejected.reason}</span>
                      <span className="text-slate-500">-${rejected.potential_revenue_lost}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Performance Metrics */}
            <Card className="p-4 bg-emerald-900/20 border-emerald-700/50">
              <h3 className="text-sm font-bold text-emerald-300 mb-3">Performance Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-400">Efficiency Score</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-emerald-500" 
                        style={{ width: `${routeData.orchestrator_response.summary.efficiency_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold text-emerald-400">
                      {(routeData.orchestrator_response.summary.efficiency_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Confidence Level</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-cyan-500" 
                        style={{ width: `${routeData.orchestrator_response.summary.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold text-cyan-400">
                      {(routeData.orchestrator_response.summary.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
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