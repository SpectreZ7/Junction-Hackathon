import { Card } from "@/components/ui/card";
import { TrendingUp, MapPin, Zap, Clock } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const Earnings = () => {
  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-2xl font-bold text-foreground">Earnings</h1>
          <p className="text-sm text-muted-foreground">Live earnings tracker</p>
        </div>

        {/* Today's Earnings */}
        <Card className="p-6 bg-gradient-earnings border-secondary/50 shadow-glow-earnings">
          <div className="text-center">
            <p className="text-sm text-white/80 mb-2">Today's Earnings</p>
            <p className="text-5xl font-bold text-white mb-2">$248.50</p>
            <div className="flex items-center justify-center gap-2 text-white/90">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm">$38.23/hour</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/20">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">18</p>
              <p className="text-xs text-white/70">Rides</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">6.5h</p>
              <p className="text-xs text-white/70">Online</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">$13.81</p>
              <p className="text-xs text-white/70">Avg/Ride</p>
            </div>
          </div>
        </Card>

        {/* Bonus Progress */}
        <Card className="p-4 bg-card border-border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-foreground">Weekly Bonus</h3>
            <span className="text-sm text-secondary font-medium">12/20 rides</span>
          </div>
          <Progress value={60} className="h-2 mb-2" />
          <p className="text-xs text-muted-foreground">8 more rides to unlock $50 bonus</p>
        </Card>

        {/* Demand Heatmap */}
        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-secondary" />
            Live Demand Map
          </h3>
          
          {/* Map Placeholder */}
          <div className="relative w-full h-48 bg-muted rounded-lg overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary/20 to-primary/20" />
            <div className="absolute top-1/3 left-1/3 w-16 h-16 bg-secondary/40 rounded-full blur-xl animate-pulse" />
            <div className="absolute top-1/2 right-1/4 w-20 h-20 bg-primary/40 rounded-full blur-xl animate-pulse" style={{ animationDelay: "0.5s" }} />
            <div className="absolute bottom-1/4 left-1/2 w-12 h-12 bg-secondary/40 rounded-full blur-xl animate-pulse" style={{ animationDelay: "1s" }} />
            
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <MapPin className="w-8 h-8 text-secondary mx-auto mb-2" />
                <p className="text-sm font-medium text-foreground">High Demand Areas</p>
                <p className="text-xs text-muted-foreground">Downtown & Airport</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Recommendations */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Smart Positioning</h2>
          
          <Card className="p-4 bg-card border-secondary/30">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0">
                <MapPin className="w-5 h-5 text-secondary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-foreground mb-1">Move to Downtown</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  2.5x surge active - high demand detected
                </p>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1 text-secondary">
                    <Clock className="w-3 h-3" />
                    <span>8 min away</span>
                  </div>
                  <div className="text-muted-foreground">
                    Est. earnings: +$60/hour
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-foreground mb-1">Airport Peak Coming</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  RAI - 15 arrivals in next hour
                </p>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1 text-primary">
                    <Clock className="w-3 h-3" />
                    <span>15 min away</span>
                  </div>
                  <div className="text-muted-foreground">
                    Queue time: 12 min
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Earnings;
