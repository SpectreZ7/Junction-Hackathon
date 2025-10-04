import { Card } from "@/components/ui/card";
import { Plane, Clock, TrendingUp, MapPin } from "lucide-react";

const Airport = () => {
  const airports = [
    {
      code: "RAI",
      name: "Raleigh-Durham",
      distance: "8.2 mi",
      eta: "15 min",
      arrivals: 12,
      peakTime: "6:30 PM",
      waitTime: "12 min",
      revenue: "$45/hr",
    },
    {
      code: "CLT",
      name: "Charlotte Douglas",
      distance: "142 mi",
      eta: "2h 15min",
      arrivals: 28,
      peakTime: "7:00 PM",
      waitTime: "8 min",
      revenue: "$52/hr",
    },
  ];

  const recentFlights = [
    { flight: "AA 1245", from: "New York", time: "6:15 PM", status: "Landing" },
    { flight: "DL 892", from: "Atlanta", time: "6:22 PM", status: "Landed" },
    { flight: "UA 456", from: "Chicago", time: "6:30 PM", status: "On Time" },
    { flight: "SW 1832", from: "Boston", time: "6:45 PM", status: "Delayed" },
  ];

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
              <p className="text-3xl font-bold text-white">{airports[0].code}</p>
              <p className="text-sm text-white/80">{airports[0].name}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-white/70">Distance</p>
                <p className="text-lg font-semibold text-white">{airports[0].distance}</p>
              </div>
              <div>
                <p className="text-xs text-white/70">ETA</p>
                <p className="text-lg font-semibold text-white">{airports[0].eta}</p>
              </div>
              <div>
                <p className="text-xs text-white/70">Arrivals</p>
                <p className="text-lg font-semibold text-white">{airports[0].arrivals} flights</p>
              </div>
              <div>
                <p className="text-xs text-white/70">Revenue</p>
                <p className="text-lg font-semibold text-white">{airports[0].revenue}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Airport List */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Nearby Airports</h2>
          
          {airports.map((airport) => (
            <Card key={airport.code} className="p-4 bg-card border-border">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-xl font-bold text-foreground">{airport.code}</h3>
                    <span className="text-xs px-2 py-1 bg-secondary/20 text-secondary rounded-full">
                      {airport.arrivals} arrivals
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{airport.name}</p>
                </div>
                <MapPin className="w-5 h-5 text-secondary" />
              </div>

              <div className="grid grid-cols-4 gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">Distance</p>
                  <p className="text-sm font-semibold text-foreground">{airport.distance}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">ETA</p>
                  <p className="text-sm font-semibold text-foreground">{airport.eta}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Wait</p>
                  <p className="text-sm font-semibold text-foreground">{airport.waitTime}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Revenue</p>
                  <p className="text-sm font-semibold text-secondary">{airport.revenue}</p>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-border flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                <span className="text-sm text-muted-foreground">
                  Peak at {airport.peakTime}
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
