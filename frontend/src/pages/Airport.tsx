import { Card } from "@/components/ui/card";
import { Plane, Clock, TrendingUp, MapPin, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { uberDriverAPI, type AirportData } from "@/lib/api";

const Airport = () => {
  const [airports, setAirports] = useState<AirportData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentCity, setCurrentCity] = useState("Amsterdam");

  useEffect(() => {
    const fetchAirportData = async () => {
      try {
        setLoading(true);
        const data = await uberDriverAPI.getAirportDemand(currentCity);
        setAirports(data.airports);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load airport data');
        console.error('Airport data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAirportData();
    
    // Refresh every 2 minutes
    const interval = setInterval(fetchAirportData, 120000);
    return () => clearInterval(interval);
  }, [currentCity]);

  const recentFlights = [
    { flight: "KL 1234", from: "New York", time: "6:15 PM", status: "Landing" },
    { flight: "AF 892", from: "Paris", time: "6:22 PM", status: "Landed" },
    { flight: "LH 456", from: "Frankfurt", time: "6:30 PM", status: "On Time" },
    { flight: "BA 1832", from: "London", time: "6:45 PM", status: "Delayed" },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-bg pb-24 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-2" />
          <p className="text-muted-foreground">Loading airport intelligence...</p>
        </div>
      </div>
    );
  }

  if (error || airports.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-bg pb-24 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-2">Error loading airport data</p>
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-2xl font-bold text-foreground">Airport Intelligence</h1>
          <p className="text-sm text-muted-foreground">Live flight tracking & revenue optimization</p>
        </div>

        {/* Best Airport Now */}
        <Card className="p-5 bg-gradient-earnings border-secondary/50 shadow-glow-earnings">
          <div className="flex items-center gap-2 mb-3">
            <Plane className="w-5 h-5 text-white" />
            <h3 className="font-semibold text-white">Recommended Now</h3>
          </div>
          
          <div className="space-y-3">
            <div>
              <p className="text-3xl font-bold text-white">{airports[0].airport_code}</p>
              <p className="text-sm text-white/80">{airports[0].airport_name}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-white/70">Wait Time</p>
                <p className="text-lg font-semibold text-white">{airports[0].expected_wait_time} min</p>
              </div>
              <div>
                <p className="text-xs text-white/70">Peak</p>
                <p className="text-lg font-semibold text-white">{airports[0].next_peak_time}</p>
              </div>
              <div>
                <p className="text-xs text-white/70">Arrivals</p>
                <p className="text-lg font-semibold text-white">{airports[0].flight_arrivals_next_hour} flights</p>
              </div>
              <div>
                <p className="text-xs text-white/70">Revenue</p>
                <p className="text-lg font-semibold text-white">${airports[0].potential_earnings_per_hour}/hr</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Airport List */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Nearby Airports</h2>
          
          {airports.map((airport) => (
            <Card key={airport.airport_code} className="p-4 bg-card border-border">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-xl font-bold text-foreground">{airport.airport_code}</h3>
                    <span className="text-xs px-2 py-1 bg-secondary/20 text-secondary rounded-full">
                      {airport.flight_arrivals_next_hour} arrivals
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{airport.airport_name}</p>
                </div>
                <div className="text-right">
                  <div className={`w-3 h-3 rounded-full ${
                    airport.peak_intensity >= 8 
                      ? "bg-red-500" 
                      : airport.peak_intensity >= 6 
                      ? "bg-yellow-500" 
                      : "bg-green-500"
                  }`} />
                  <MapPin className="w-5 h-5 text-secondary" />
                </div>
              </div>

              <div className="grid grid-cols-4 gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">Priority</p>
                  <p className="text-sm font-semibold text-foreground">{airport.recommendation_priority.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Peak</p>
                  <p className="text-sm font-semibold text-foreground">{airport.peak_intensity.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Wait</p>
                  <p className="text-sm font-semibold text-foreground">{airport.expected_wait_time}min</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Revenue</p>
                  <p className="text-sm font-semibold text-secondary">${airport.potential_earnings_per_hour}/hr</p>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-border flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                <span className="text-sm text-muted-foreground">
                  Peak at {airport.next_peak_time}
                </span>
              </div>
            </Card>
          ))}
        </div>

        {/* Live Arrivals */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Live Arrivals - RAI</h2>
          
          <Card className="p-4 bg-card border-border">
            <div className="space-y-3">
              {recentFlights.map((flight) => (
                <div key={flight.flight} className="flex items-center justify-between py-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-foreground">{flight.flight}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        flight.status === "Landing" 
                          ? "bg-success/20 text-success"
                          : flight.status === "Landed"
                          ? "bg-primary/20 text-primary"
                          : flight.status === "Delayed"
                          ? "bg-destructive/20 text-destructive"
                          : "bg-secondary/20 text-secondary"
                      }`}>
                        {flight.status}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">From {flight.from}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">{flight.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Airport;
