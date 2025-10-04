import { Switch } from "@/components/ui/switch";
import { Card } from "@/components/ui/card";
import { Brain, TrendingUp, Plane, Heart, Star, Clock, Target } from "lucide-react";
import { useState } from "react";

const Dashboard = () => {
  const [isOnline, setIsOnline] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pt-2">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
            <p className="text-sm text-muted-foreground">Welcome back, Driver</p>
          </div>
          <div className="w-12 h-12 rounded-full bg-gradient-ai flex items-center justify-center text-white font-bold">
            JD
          </div>
        </div>

        {/* Status Card */}
        <Card className="p-5 bg-card border-border animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <p className="text-lg font-semibold text-foreground">
                {isOnline ? "Online" : "Offline"}
              </p>
            </div>
            <Switch checked={isOnline} onCheckedChange={setIsOnline} />
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div>
              <p className="text-2xl font-bold text-secondary">$248</p>
              <p className="text-xs text-muted-foreground">Today</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">6.5h</p>
              <p className="text-xs text-muted-foreground">Hours</p>
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-4 h-4 text-success" />
              <div>
                <p className="text-2xl font-bold text-success">85</p>
                <p className="text-xs text-muted-foreground">Health</p>
              </div>
            </div>
          </div>
        </Card>

        {/* AI Recommendations */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            AI Recommendations
          </h2>

          <Card className="p-4 bg-gradient-ai border-primary/50 shadow-glow-ai animate-slide-up">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-white mb-1">Digital Twin Strategy</h3>
                <p className="text-sm text-white/90 mb-2">
                  Switch to Early Bird schedule for 18% earnings boost
                </p>
                <div className="flex items-center gap-2 text-xs text-white/80">
                  <TrendingUp className="w-3 h-3" />
                  <span>Projected: $312/day</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-secondary/30 animate-slide-up" style={{ animationDelay: "0.1s" }}>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0">
                <Plane className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-1">Airport Opportunity</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  RAI peak in 45 minutes - 12 arrivals expected
                </p>
                <div className="flex items-center gap-2 text-xs text-secondary">
                  <Clock className="w-3 h-3" />
                  <span>15 min drive</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-success/30 animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                <Heart className="w-5 h-5 text-success" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-1">Wellbeing Alert</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Take a 15-minute break soon - fatigue level rising
                </p>
                <div className="flex items-center gap-2 text-xs text-success">
                  <Target className="w-3 h-3" />
                  <span>Optimal performance</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Today's Stats</h2>
          <div className="grid grid-cols-2 gap-3">
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Rides</p>
              <p className="text-3xl font-bold text-foreground mt-1">18</p>
              <p className="text-xs text-success mt-1">+3 from yesterday</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Rating</p>
              <div className="flex items-center gap-1 mt-1">
                <p className="text-3xl font-bold text-foreground">4.9</p>
                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
              </div>
              <p className="text-xs text-muted-foreground mt-1">Excellent</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Acceptance</p>
              <p className="text-3xl font-bold text-foreground mt-1">94%</p>
              <p className="text-xs text-success mt-1">Above target</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Avg/Hour</p>
              <p className="text-3xl font-bold text-secondary mt-1">$38</p>
              <p className="text-xs text-secondary mt-1">Peak rate</p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
