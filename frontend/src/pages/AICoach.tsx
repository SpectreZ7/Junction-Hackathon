import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { TrendingUp, Clock, Zap, Calendar, Target } from "lucide-react";

const AICoach = () => {
  const strategies = [
    { name: "Current", earnings: "$248", hours: "8h", fatigue: "Medium" },
    { name: "Early Bird", earnings: "$312", hours: "7.5h", fatigue: "Low" },
    { name: "Surge Hunter", earnings: "$385", hours: "9h", fatigue: "High" },
    { name: "Consistent", earnings: "$280", hours: "8h", fatigue: "Low" },
  ];

  const weekSchedule = [
    { day: "Mon", hours: [6, 7, 8, 16, 17, 18] },
    { day: "Tue", hours: [6, 7, 8, 16, 17, 18] },
    { day: "Wed", hours: [6, 7, 8, 16, 17, 18] },
    { day: "Thu", hours: [6, 7, 8, 16, 17, 18] },
    { day: "Fri", hours: [6, 7, 8, 16, 17, 18, 19] },
    { day: "Sat", hours: [10, 11, 12, 18, 19, 20, 21] },
    { day: "Sun", hours: [10, 11, 12, 18, 19, 20] },
  ];

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-2xl font-bold text-foreground">AI Coach</h1>
          <p className="text-sm text-muted-foreground">Your Digital Twin Strategist</p>
        </div>

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
          
          <Tabs defaultValue="current" className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-muted">
              <TabsTrigger value="current">Current</TabsTrigger>
              <TabsTrigger value="early">Early Bird</TabsTrigger>
              <TabsTrigger value="surge">Surge</TabsTrigger>
              <TabsTrigger value="consistent">Steady</TabsTrigger>
            </TabsList>
            
            {strategies.map((strategy, idx) => (
              <TabsContent 
                key={strategy.name} 
                value={strategy.name.toLowerCase().replace(" ", "")}
                className="space-y-3"
              >
                <Card className="p-5 bg-gradient-ai border-primary/50 shadow-glow-ai">
                  <h3 className="text-lg font-bold text-white mb-4">{strategy.name} Strategy</h3>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-white/70">Earnings</p>
                      <p className="text-2xl font-bold text-white">{strategy.earnings}</p>
                      <div className="flex items-center gap-1 text-xs text-white/90 mt-1">
                        <TrendingUp className="w-3 h-3" />
                        +18%
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Hours</p>
                      <p className="text-2xl font-bold text-white">{strategy.hours}</p>
                      <div className="flex items-center gap-1 text-xs text-white/90 mt-1">
                        <Clock className="w-3 h-3" />
                        -0.5h
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Fatigue</p>
                      <p className="text-2xl font-bold text-white">{strategy.fatigue}</p>
                      <div className="flex items-center gap-1 text-xs text-success mt-1">
                        <Target className="w-3 h-3" />
                        Better
                      </div>
                    </div>
                  </div>

                  <Button className="w-full mt-4 bg-white text-primary hover:bg-white/90">
                    Try This Week
                  </Button>
                </Card>

                <Card className="p-4 bg-card border-border">
                  <h4 className="text-sm font-semibold text-foreground mb-3">Key Changes</h4>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Start at 6 AM instead of 8 AM for morning surge
                      </span>
                    </li>
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Focus on airport runs during peak arrival times
                      </span>
                    </li>
                    <li className="flex items-start gap-2 text-sm">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        Take strategic breaks to maintain energy levels
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
