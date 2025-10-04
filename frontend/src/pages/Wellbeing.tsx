import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Heart, Moon, Coffee, Activity, Phone, CheckCircle, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { uberDriverAPI, type WellbeingCheckIn } from "@/lib/api";

const Wellbeing = () => {
  const [mood, setMood] = useState([4]); // 1-5 scale
  const [fatigue, setFatigue] = useState([2]); // 1-5 scale
  const [stress, setStress] = useState([2]); // 1-5 scale
  const [bodyDiscomfort, setBodyDiscomfort] = useState([2]); // 1-5 scale
  const [sleep, setSleep] = useState([7]); // hours
  const [wellbeingScore, setWellbeingScore] = useState(85);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastCheckIn, setLastCheckIn] = useState<string | null>(null);

  const driverId = "E10156";

  useEffect(() => {
    const fetchWellbeingStatus = async () => {
      try {
        // First check localStorage for updated score
        const storedScore = localStorage.getItem('wellbeingScore');
        const storedCheckIn = localStorage.getItem('lastWellbeingCheckIn');
        
        if (storedScore) {
          setWellbeingScore(parseFloat(storedScore));
        }
        if (storedCheckIn) {
          setLastCheckIn(storedCheckIn);
        }

        // Still fetch from API for suggestions and other data
        const status = await uberDriverAPI.getWellbeingStatus(driverId);
        
        // Only update score if no stored value exists
        if (!storedScore) {
          setWellbeingScore(status.current_score);
        }
        
        setSuggestions(status.recommendations);
        
        // Only update last check-in if no stored value exists
        if (!storedCheckIn) {
          setLastCheckIn(status.last_checkin);
        }
      } catch (err) {
        console.error('Failed to fetch wellbeing status:', err);
      }
    };

    fetchWellbeingStatus();
  }, [driverId]);

  const handleCheckIn = async () => {
    try {
      setLoading(true);
      
      const checkInData: WellbeingCheckIn = {
        driver_id: driverId,
        sleep_hours: sleep[0],
        fatigue_level: fatigue[0],
        stress_level: stress[0],
        body_discomfort: bodyDiscomfort[0],
        mood: mood[0]
      };

      const response = await uberDriverAPI.submitWellbeingCheckIn(checkInData);
      
      // Update local state
      setWellbeingScore(response.wellbeing_score);
      setSuggestions(response.suggestions);
      setLastCheckIn(new Date().toISOString());

      // Store in localStorage for persistence across pages
      localStorage.setItem('wellbeingScore', response.wellbeing_score.toString());
      localStorage.setItem('lastWellbeingCheckIn', new Date().toISOString());
      
      // No popup - just silent success
      
    } catch (err) {
      console.error('Check-in failed:', err);
      alert('Failed to submit check-in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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

        {/* Last Check-In Info */}
        {lastCheckIn && (
          <Card className="p-3 bg-muted/50 border-border">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-success" />
              <p className="text-sm text-muted-foreground">
                Last check-in: {new Date(lastCheckIn).toLocaleString()}
              </p>
            </div>
          </Card>
        )}

        {/* Quick Check-In */}
        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold text-foreground mb-4">Quick Check-In</h3>
          
          <div className="space-y-5">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Mood (1-5)</span>
                <span className="text-sm font-medium text-foreground">{mood[0]}</span>
              </div>
              <Slider
                value={mood}
                onValueChange={setMood}
                max={5}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Poor</span>
                <span>Excellent</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Fatigue Level (1-5)</span>
                <span className="text-sm font-medium text-foreground">{fatigue[0]}</span>
              </div>
              <Slider
                value={fatigue}
                onValueChange={setFatigue}
                max={5}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Alert</span>
                <span>Exhausted</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Stress Level (1-5)</span>
                <span className="text-sm font-medium text-foreground">{stress[0]}</span>
              </div>
              <Slider
                value={stress}
                onValueChange={setStress}
                max={5}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Relaxed</span>
                <span>Very Stressed</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Body Discomfort (1-5)</span>
                <span className="text-sm font-medium text-foreground">{bodyDiscomfort[0]}</span>
              </div>
              <Slider
                value={bodyDiscomfort}
                onValueChange={setBodyDiscomfort}
                max={5}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Comfortable</span>
                <span>Very Uncomfortable</span>
              </div>
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
                min={3}
                step={0.5}
                className="w-full"
              />
            </div>
          </div>

          <Button 
            onClick={handleCheckIn}
            disabled={loading}
            className="w-full mt-4 bg-success hover:bg-success/90"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Processing...
              </>
            ) : (
              'Save Check-In'
            )}
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
          <h2 className="text-lg font-semibold text-foreground">AI Recommendations</h2>
          
          {suggestions.map((suggestion, index) => (
            <Card key={index} className="p-4 bg-card border-success/30">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                  {index === 0 ? <Coffee className="w-5 h-5 text-success" /> : 
                   index === 1 ? <Activity className="w-5 h-5 text-secondary" /> :
                   <Heart className="w-5 h-5 text-primary" />}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground mb-1">Wellbeing Tip</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {suggestion}
                  </p>
                  <Button size="sm" variant="outline" className="border-success text-success hover:bg-success/10">
                    Apply Suggestion
                  </Button>
                </div>
              </div>
            </Card>
          ))}

          {suggestions.length === 0 && (
            <Card className="p-4 bg-card border-success/30">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                  <Heart className="w-5 h-5 text-success" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Keep up the good work!</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Your wellbeing is on track. Complete a check-in to get personalized recommendations.
                  </p>
                </div>
              </div>
            </Card>
          )}
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
