import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Heart, Moon, Coffee, Activity, Phone } from "lucide-react";
import { useState } from "react";

const Wellbeing = () => {
  const [mood, setMood] = useState([70]);
  const [fatigue, setFatigue] = useState([40]);
  const [stress, setStress] = useState([50]);
  const [sleep, setSleep] = useState([6]);

  const wellbeingScore = Math.round((mood[0] + (100 - fatigue[0]) + (100 - stress[0]) + (sleep[0] / 10) * 100) / 4);

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-secondary";
    if (score >= 40) return "text-yellow-500";
    return "text-destructive";
  };

  const getScoreStatus = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Needs Attention";
  };

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-2xl font-bold text-foreground">Wellbeing Monitor</h1>
          <p className="text-sm text-muted-foreground">Track and improve your health</p>
        </div>

        {/* Wellbeing Score */}
        <Card className="p-6 bg-gradient-wellbeing border-success/50 shadow-glow-wellbeing">
          <div className="text-center">
            <Heart className="w-12 h-12 text-white mx-auto mb-3" />
            <p className="text-sm text-white/80 mb-2">Overall Wellbeing Score</p>
            <p className="text-6xl font-bold text-white mb-2">{wellbeingScore}</p>
            <p className="text-lg text-white/90">{getScoreStatus(wellbeingScore)}</p>
          </div>
        </Card>

        {/* Quick Check-In */}
        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold text-foreground mb-4">Quick Check-In</h3>
          
          <div className="space-y-5">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Mood</span>
                <span className="text-sm font-medium text-foreground">{mood[0]}%</span>
              </div>
              <Slider
                value={mood}
                onValueChange={setMood}
                max={100}
                step={1}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Fatigue Level</span>
                <span className="text-sm font-medium text-foreground">{fatigue[0]}%</span>
              </div>
              <Slider
                value={fatigue}
                onValueChange={setFatigue}
                max={100}
                step={1}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Stress Level</span>
                <span className="text-sm font-medium text-foreground">{stress[0]}%</span>
              </div>
              <Slider
                value={stress}
                onValueChange={setStress}
                max={100}
                step={1}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Sleep Hours (last night)</span>
                <span className="text-sm font-medium text-foreground">{sleep[0]}h</span>
              </div>
              <Slider
                value={sleep}
                onValueChange={setSleep}
                max={12}
                step={0.5}
                className="w-full"
              />
            </div>
          </div>

          <Button className="w-full mt-4 bg-success hover:bg-success/90">
            Save Check-In
          </Button>
        </Card>

        {/* Trends */}
        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold text-foreground mb-3">This Week's Trends</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <Moon className="w-5 h-5 text-secondary" />
                <div>
                  <p className="text-sm font-medium text-foreground">Sleep Quality</p>
                  <p className="text-xs text-muted-foreground">Avg 6.5 hours/night</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-secondary">+12%</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-success" />
                <div>
                  <p className="text-sm font-medium text-foreground">Energy Levels</p>
                  <p className="text-xs text-muted-foreground">Stable throughout day</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-success">Good</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <Coffee className="w-5 h-5 text-yellow-500" />
                <div>
                  <p className="text-sm font-medium text-foreground">Break Frequency</p>
                  <p className="text-xs text-muted-foreground">Every 2.3 hours</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-foreground">Optimal</span>
            </div>
          </div>
        </Card>

        {/* Smart Recommendations */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Recommendations</h2>
          
          <Card className="p-4 bg-card border-success/30">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                <Coffee className="w-5 h-5 text-success" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-1">Take a Break Soon</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  You've been driving for 2.5 hours. A 10-minute break will improve focus and safety.
                </p>
                <Button size="sm" variant="outline" className="border-success text-success hover:bg-success/10">
                  Start Break Timer
                </Button>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-1">Quick Stretch Exercise</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  5-minute guided stretching to reduce back tension
                </p>
                <Button size="sm" variant="outline" className="border-secondary text-secondary hover:bg-secondary/10">
                  Start Exercise
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Emergency Contact */}
        <Card className="p-4 bg-destructive/10 border-destructive/30">
          <div className="flex items-center gap-3">
            <Phone className="w-5 h-5 text-destructive" />
            <div className="flex-1">
              <h3 className="font-semibold text-foreground">Emergency Support</h3>
              <p className="text-sm text-muted-foreground">Available 24/7 for driver assistance</p>
            </div>
            <Button size="sm" variant="destructive">
              Call Now
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Wellbeing;
