import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { TrendingUp, Clock, Zap, Calendar, Target, Loader2, Brain } from "lucide-react";
import { useState, useEffect } from "react";
import { uberDriverAPI, type DigitalTwinProfile, type OptimizationScenario } from "@/lib/api";

const AICoach = () => {
  const [profile, setProfile] = useState<DigitalTwinProfile | null>(null);
  const [scenarios, setScenarios] = useState<OptimizationScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedScenario, setSelectedScenario] = useState("current");

  const driverId = "E10156";

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch profile and optimization data in parallel
        const [profileData, optimizationData] = await Promise.all([
          uberDriverAPI.getDigitalTwinProfile(driverId),
          uberDriverAPI.optimizeSchedule(driverId)
        ]);
        
        setProfile(profileData.profile);
        setScenarios(optimizationData.scenarios);
        
        // Set the best scenario as default
        setSelectedScenario(optimizationData.best_scenario.toLowerCase().replace(/\s+/g, ""));
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load AI coach data');
        console.error('AI Coach data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [driverId]);

  const generateWeekSchedule = (preferredHours: number[]) => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    return days.map(day => ({
      day,
      hours: preferredHours // Simplified - in a real app, this would be more sophisticated
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-bg pb-24 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-2" />
          <p className="text-muted-foreground">Analyzing your patterns...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gradient-bg pb-24 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-2">Error loading AI coach</p>
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  const weekSchedule = generateWeekSchedule(profile.preferred_hours);

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            AI Coach
          </h1>
          <p className="text-sm text-muted-foreground">Your Digital Twin Strategist</p>
        </div>

        {/* Profile Stats */}
        <Card className="p-4 bg-card border-primary/30">
          <h3 className="text-sm font-semibold text-foreground mb-3">Your AI Profile</h3>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-primary">${profile.avg_earnings_per_hour}</p>
              <p className="text-xs text-muted-foreground">Avg/Hour</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-secondary">{profile.consistency_score.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">Consistency</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-success">{profile.total_weekly_hours}h</p>
              <p className="text-xs text-muted-foreground">Weekly Hours</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{profile.surge_responsiveness.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground">Surge Response</p>
            </div>
          </div>
        </Card>

        {/* Weekly Heatmap */}
        <Card className="p-4 bg-card border-primary/30">
          <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-primary" />
            Your Peak Hours
          </h3>
          <div className="space-y-2">
            {weekSchedule.map((day) => (
              <div key={day.day} className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-8">{day.day}</span>
                <div className="flex-1 flex gap-1">
                  {Array.from({ length: 24 }, (_, i) => (
                    <div
                      key={i}
                      className={`h-6 flex-1 rounded-sm ${
                        day.hours.includes(i)
                          ? "bg-gradient-ai shadow-glow-ai"
                          : "bg-muted/30"
                      }`}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Strategy Comparison */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Strategy Scenarios</h2>
          
          <Tabs value={selectedScenario} onValueChange={setSelectedScenario} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-muted">
              {scenarios.slice(0, 2).map((scenario) => (
                <TabsTrigger 
                  key={scenario.name} 
                  value={scenario.name.toLowerCase().replace(/\s+/g, "")}
                  className="text-xs"
                >
                  {scenario.name.replace("Pattern", "").replace("(Optimized)", "").trim()}
                </TabsTrigger>
              ))}
            </TabsList>
            
            {scenarios.map((scenario) => (
              <TabsContent 
                key={scenario.name} 
                value={scenario.name.toLowerCase().replace(/\s+/g, "")}
                className="space-y-3"
              >
                <Card className="p-5 bg-gradient-ai border-primary/50 shadow-glow-ai">
                  <h3 className="text-lg font-bold text-white mb-4">{scenario.name}</h3>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-white/70">Earnings</p>
                      <p className="text-2xl font-bold text-white">${scenario.projected_earnings}</p>
                      <div className="flex items-center gap-1 text-xs text-white/90 mt-1">
                        <TrendingUp className="w-3 h-3" />
                        +{scenario.improvement.toFixed(0)}%
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Feasibility</p>
                      <p className="text-2xl font-bold text-white">{(scenario.feasibility * 100).toFixed(0)}%</p>
                      <div className="flex items-center gap-1 text-xs text-white/90 mt-1">
                        <Clock className="w-3 h-3" />
                        {scenario.feasibility > 0.8 ? 'Easy' : scenario.feasibility > 0.6 ? 'Medium' : 'Hard'}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Boost</p>
                      <p className="text-2xl font-bold text-white">${(scenario.projected_earnings - scenarios[0]?.projected_earnings || 0).toFixed(0)}</p>
                      <div className="flex items-center gap-1 text-xs text-success mt-1">
                        <Target className="w-3 h-3" />
                        Weekly
                      </div>
                    </div>
                  </div>

                  <Button className="w-full mt-4 bg-white text-primary hover:bg-white/90">
                    Try This Week
                  </Button>
                </Card>

                <Card className="p-4 bg-card border-border">
                  <h4 className="text-sm font-semibold text-foreground mb-3">Strategy Details</h4>
                  <p className="text-sm text-muted-foreground mb-3">{scenario.description}</p>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Improvement potential: {scenario.improvement.toFixed(1)}%
                      </span>
                    </li>
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Feasibility score: {(scenario.feasibility * 100).toFixed(0)}%
                      </span>
                    </li>
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Based on your historical patterns and preferences
                      </span>
                    </li>
                  </ul>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default AICoach;
