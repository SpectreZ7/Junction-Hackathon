import { Card } from "@/components/ui/card";
import { Plane, Clock, RefreshCw, Zap, Moon, Music, Users, MapPin, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";

// Types basés sur votre API
interface Peak {
  peak_id: string;
  time_window: string;
  num_flights: number;
  terminals: string[];
  estimated_passengers: number;
  priority: string;
  priority_score: number;
  estimated_revenue: number;
  estimated_wait_minutes: number;
  is_recommended: boolean;
}

interface AirportData {
  agent_id: string;
  agent_type: string;
  timestamp: string;
  priority: number;
  status?: string;
  message?: string;
  all_peaks: Peak[];
  best_recommendation: {
    action: string;
    target_peak: string;
    location: {
      type: string;
      code: string;
      arrival_time: string;
    };
    expected_revenue: number;
    duration_minutes: number;
    confidence: number;
    reasoning: string;
  } | null;
  metadata?: {
    total_peaks_detected: number;
    flights_analyzed: number;
    airport_code: string;
  };
}

interface APIResponse {
  city: string;
  timestamp: string;
  airports: Record<string, AirportData>;
}

interface EventPeak {
  peak_id: string;
  time_window: string;
  event_name: string;
  venue_name: string;
  estimated_attendees: number;
  priority: string;
  is_recommended: boolean;
}

interface EventData {
  agent_id: string;
  agent_type: string;
  timestamp: string;
  priority: number;
  all_peaks: EventPeak[];
  best_recommendation: {
    action: string;
    target_peak: string;
    reasoning: string;
  } | null;
  metadata: {
    total_peaks_detected: number;
    events_analyzed: number;
  };
}

interface EventAPIResponse {
  city: string;
  timestamp: string;
  events: EventData;
}

const Hotspots = () => {
  const [apiData, setApiData] = useState<APIResponse | null>(null);
  const [eventData, setEventData] = useState<EventAPIResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [eventError, setEventError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [lastEventUpdate, setLastEventUpdate] = useState<string>("");

  const fetchHotspotData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://127.0.0.1:1000/all_airports');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: APIResponse = await response.json();
      setApiData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      console.error('API fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEventData = async () => {
    try {
      setLoadingEvents(true);
      setEventError(null);
      
      const response = await fetch('http://127.0.0.1:1001/all_events');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: EventAPIResponse = await response.json();
      setEventData(data);
      setLastEventUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setEventError(err instanceof Error ? err.message : 'Failed to load event data');
      console.error('Event API fetch error:', err);
    } finally {
      setLoadingEvents(false);
    }
  };

  useEffect(() => {
    fetchHotspotData();
    fetchEventData();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getEventPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-purple-500';
      case 'medium': return 'bg-pink-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getEventSize = (attendees: number) => {
    if (attendees >= 10000) return { size: 'Massive', color: 'text-purple-400' };
    if (attendees >= 5000) return { size: 'Large', color: 'text-pink-400' };
    if (attendees >= 2000) return { size: 'Medium', color: 'text-blue-400' };
    return { size: 'Small', color: 'text-slate-400' };
  };

  const getActivityLevel = (airport: AirportData) => {
    if (airport.status === 'no_flights' || airport.all_peaks.length === 0) {
      return { level: 'Quiet', color: 'text-slate-500', icon: Moon };
    }
    
    const highPriorityPeaks = airport.all_peaks.filter(p => p.priority === 'high').length;
    
    if (highPriorityPeaks >= 2) {
      return { level: 'Very Busy', color: 'text-red-500', icon: Zap };
    } else if (highPriorityPeaks >= 1) {
      return { level: 'Busy', color: 'text-yellow-500', icon: Plane };
    } else if (airport.all_peaks.length > 0) {
      return { level: 'Moderate', color: 'text-blue-500', icon: Clock };
    }
    
    return { level: 'Quiet', color: 'text-slate-500', icon: Moon };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header with Refresh */}
        <div className="pt-2">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl font-bold text-white">Airport Intelligence</h1>
              {apiData && <p className="text-sm text-slate-400">{apiData.city}</p>}
            </div>
            <button
              onClick={fetchHotspotData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white rounded-lg transition-all duration-200 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>
          {lastUpdate && (
            <p className="text-xs text-slate-500">Last update: {lastUpdate}</p>
          )}
        </div>

        {/* Thinking Animation */}
        {loading && (
          <Card className="p-6 bg-slate-800/50 border-slate-700">
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0s' }}></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
              <p className="text-slate-400 text-sm animate-pulse">Analyzing airport data...</p>
            </div>
          </Card>
        )}

        {/* Error Display */}
        {error && !loading && (
          <Card className="p-4 bg-red-900/20 border-red-500/50">
            <p className="text-red-400 text-sm">{error}</p>
          </Card>
        )}

        {/* Airport Cards */}
        {!loading && apiData && (
          <div className="space-y-3">
            {Object.entries(apiData.airports).map(([code, airport]) => {
              const activity = getActivityLevel(airport);
              const ActivityIcon = activity.icon;
              const nextPeaks = airport.all_peaks.slice(0, 3);
              
              return (
                <Card key={code} className="p-4 bg-slate-800/50 border-slate-700 backdrop-blur-sm hover:bg-slate-800/70 transition-all">
                  {/* Airport Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-2xl font-bold text-white">{code}</h3>
                        <ActivityIcon className={`w-5 h-5 ${activity.color}`} />
                      </div>
                      <p className={`text-sm font-medium ${activity.color}`}>{activity.level}</p>
                    </div>
                    <div className="text-right">
                      {airport.status !== 'no_flights' && (
                        <div className="text-xs text-slate-400">
                          <p>{airport.metadata?.flights_analyzed || 0} flights</p>
                          <p>{airport.metadata?.total_peaks_detected || 0} peaks</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* No Activity Message */}
                  {(airport.status === 'no_flights' || airport.all_peaks.length === 0) && (
                    <div className="py-3 text-center">
                      <Moon className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                      <p className="text-slate-500 text-sm">{airport.message || 'No activity in the next 12 hours'}</p>
                    </div>
                  )}

                  {/* Upcoming Peaks */}
                  {nextPeaks.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-blue-400" />
                        <h4 className="text-xs font-semibold text-slate-400 uppercase">Next Hours</h4>
                      </div>
                      
                      {nextPeaks.map((peak) => (
                        <div 
                          key={peak.peak_id} 
                          className={`p-3 rounded-lg border ${
                            peak.is_recommended 
                              ? 'bg-blue-500/10 border-blue-500/50' 
                              : 'bg-slate-700/30 border-slate-600/30'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-white">{peak.time_window}</span>
                              {peak.is_recommended && (
                                <span className="text-xs px-2 py-0.5 bg-blue-500 text-white rounded-full font-medium">
                                  Best
                                </span>
                              )}
                            </div>
                            <div className={`w-2 h-2 rounded-full ${getPriorityColor(peak.priority)}`} />
                          </div>
                          
                          <div className="grid grid-cols-4 gap-2 text-xs">
                            <div>
                              <p className="text-slate-500">Flights</p>
                              <p className="text-white font-semibold">{peak.num_flights}</p>
                            </div>
                            <div>
                              <p className="text-slate-500">Pax</p>
                              <p className="text-white font-semibold">{peak.estimated_passengers}</p>
                            </div>
                            <div>
                              <p className="text-slate-500">Wait</p>
                              <p className="text-white font-semibold">{peak.estimated_wait_minutes}m</p>
                            </div>
                            <div>
                              <p className="text-slate-500">Rev</p>
                              <p className="text-green-400 font-semibold">${peak.estimated_revenue}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}

        {/* Divider */}
        {!loading && apiData && (
          <div className="flex items-center gap-3 py-4">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent"></div>
            <Music className="w-5 h-5 text-purple-400" />
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent"></div>
          </div>
        )}

        {/* Event Planning Section */}
        <div className="space-y-4">
          {/* Event Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Music className="w-6 h-6 text-purple-400" />
              <div>
                <h2 className="text-xl font-bold text-white">Event Planning</h2>
                <p className="text-xs text-slate-400">Live events & venue intelligence</p>
              </div>
            </div>
            <button
              onClick={fetchEventData}
              disabled={loadingEvents}
              className="flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white rounded-lg transition-all duration-200 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${loadingEvents ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>

          {lastEventUpdate && (
            <p className="text-xs text-slate-500">Last update: {lastEventUpdate}</p>
          )}

          {/* Thinking Animation for Events */}
          {loadingEvents && (
            <Card className="p-6 bg-purple-900/20 border-purple-700/50">
              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0s' }}></div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <p className="text-purple-400 text-sm animate-pulse">Analyzing event data...</p>
              </div>
            </Card>
          )}

          {/* Event Error Display */}
          {eventError && !loadingEvents && (
            <Card className="p-4 bg-purple-900/20 border-purple-500/50">
              <p className="text-purple-400 text-sm">{eventError}</p>
            </Card>
          )}

          {/* Best Event Recommendation */}
          {!loadingEvents && eventData && eventData.events.best_recommendation && (
            <Card className="p-5 bg-gradient-to-br from-purple-600 to-pink-600 border-purple-500/50 shadow-lg shadow-purple-500/20">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-white" />
                <h3 className="font-semibold text-white">Top Event Opportunity</h3>
              </div>
              
              <div className="space-y-2">
                {eventData.events.all_peaks
                  .filter(p => p.is_recommended)
                  .map(peak => (
                    <div key={peak.peak_id}>
                      <p className="text-2xl font-bold text-white mb-1">{peak.event_name}</p>
                      <div className="flex items-center gap-2 text-white/90 text-sm mb-2">
                        <MapPin className="w-4 h-4" />
                        <span>{peak.venue_name}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <p className="text-white/70 text-xs">Time</p>
                          <p className="text-white font-semibold">{peak.time_window}</p>
                        </div>
                        <div>
                          <p className="text-white/70 text-xs">Attendees</p>
                          <p className="text-white font-semibold">{peak.estimated_attendees.toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                <p className="text-white/80 text-sm mt-3">
                  {eventData.events.best_recommendation.reasoning}
                </p>
              </div>
            </Card>
          )}

          {/* All Events List */}
          {!loadingEvents && eventData && eventData.events.all_peaks.length > 0 && (
            <Card className="p-4 bg-purple-900/20 border-purple-700/50 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Upcoming Events</h3>
                <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full">
                  {eventData.events.metadata.events_analyzed} events
                </span>
              </div>

              <div className="space-y-3">
                {eventData.events.all_peaks.map((event) => {
                  const eventSize = getEventSize(event.estimated_attendees);
                  
                  return (
                    <div 
                      key={event.peak_id}
                      className={`p-3 rounded-lg border transition-all ${
                        event.is_recommended
                          ? 'bg-purple-500/10 border-purple-500/50'
                          : 'bg-slate-800/30 border-slate-700/30'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-white text-sm">{event.event_name}</h4>
                            {event.is_recommended && (
                              <span className="text-xs px-2 py-0.5 bg-purple-500 text-white rounded-full font-medium">
                                Best
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            <MapPin className="w-3 h-3" />
                            <span>{event.venue_name}</span>
                          </div>
                        </div>
                        <div className={`w-2 h-2 rounded-full ${getEventPriorityColor(event.priority)}`} />
                      </div>

                      <div className="grid grid-cols-3 gap-3 mt-3 text-xs">
                        <div>
                          <p className="text-slate-500">Time</p>
                          <p className="text-white font-semibold">{event.time_window}</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Size</p>
                          <p className={`font-semibold ${eventSize.color}`}>{eventSize.size}</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Attendees</p>
                          <p className="text-purple-400 font-semibold">{(event.estimated_attendees / 1000).toFixed(1)}k</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* No Events Message */}
          {!loadingEvents && eventData && eventData.events.all_peaks.length === 0 && (
            <Card className="p-6 bg-purple-900/20 border-purple-700/50">
              <div className="text-center">
                <Moon className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <p className="text-purple-400 text-sm">No events scheduled</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Hotspots;