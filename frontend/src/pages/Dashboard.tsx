import { Switch } from "@/components/ui/switch";
import { Card } from "@/components/ui/card";
import { Brain, TrendingUp, Plane, Heart, Star, Clock, Target, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { uberDriverAPI, type DashboardData } from "@/lib/api";

const Dashboard = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const driverId = "E10156"; // Default driver ID

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await uberDriverAPI.getDashboardData(driverId);
        
        // Check for updated wellbeing score in localStorage
        const storedWellbeingScore = localStorage.getItem('wellbeingScore');
        if (storedWellbeingScore) {
          // Update the wellbeing score in the dashboard data
          data.status.wellbeing_score = parseFloat(storedWellbeingScore);
        }
        
        setDashboardData(data);
        setIsOnline(data.status.is_online);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [driverId]);

  if (loading) {
    return (
      <div className="h-full bg-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-2" />
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="h-full bg-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-2">Error loading dashboard</p>
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pt-2">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
            <p className="text-sm text-muted-foreground">Welcome back, Driver {dashboardData.driver_id}</p>
          </div>
          <div className="w-12 h-12 rounded-full bg-gradient-ai flex items-center justify-center text-white font-bold">
            E
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
            <div className="text-center">
              <p className="text-2xl font-bold text-secondary">${dashboardData.status.earnings_today}</p>
              <p className="text-xs text-muted-foreground">Today</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">{dashboardData.status.hours_worked}h</p>
              <p className="text-xs text-muted-foreground">Hours</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Heart className="w-4 h-4 text-success" />
                <p className="text-2xl font-bold text-success">{dashboardData.status.wellbeing_score}</p>
              </div>
              <p className="text-xs text-muted-foreground">Health</p>
            </div>
          </div>
        </Card>

        {/* AI Recommendations */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            AI Recommendations
          </h2>

          {dashboardData.recommendations.map((recommendation, index) => {
            const getIcon = (type: string) => {
              switch (type) {
                case 'digital_twin': return <Brain className="w-5 h-5 text-white" />;
                case 'airport': return <Plane className="w-5 h-5 text-secondary" />;
                case 'wellbeing': return <Heart className="w-5 h-5 text-success" />;
                default: return <Brain className="w-5 h-5 text-white" />;
              }
            };

            const getCardStyle = (type: string) => {
              switch (type) {
                case 'digital_twin': 
                  return "p-4 bg-gradient-ai border-primary/50 shadow-glow-ai animate-slide-up";
                case 'airport': 
                  return "p-4 bg-card border-secondary/30 animate-slide-up";
                case 'wellbeing': 
                  return "p-4 bg-card border-success/30 animate-slide-up";
                default: 
                  return "p-4 bg-card border-border animate-slide-up";
              }
            };

            const getIconBgStyle = (type: string) => {
              switch (type) {
                case 'digital_twin': 
                  return "w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0";
                case 'airport': 
                  return "w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0";
                case 'wellbeing': 
                  return "w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0";
                default: 
                  return "w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0";
              }
            };

            const getTextStyle = (type: string) => {
              return type === 'digital_twin' ? 'text-white' : 'text-foreground';
            };

            const getSubTextStyle = (type: string) => {
              return type === 'digital_twin' ? 'text-white/90' : 'text-muted-foreground';
            };

            return (
              <Card key={index} className={getCardStyle(recommendation.type)} style={{ animationDelay: `${index * 0.1}s` }}>
                <div className="flex items-start gap-3">
                  <div className={getIconBgStyle(recommendation.type)}>
                    {getIcon(recommendation.type)}
                  </div>
                  <div>
                    <h3 className={`font-semibold mb-1 ${getTextStyle(recommendation.type)}`}>
                      {recommendation.title}
                    </h3>
                    <p className={`text-sm mb-2 ${getSubTextStyle(recommendation.type)}`}>
                      {recommendation.message}
                    </p>
                    <div className={`flex items-center gap-2 text-xs ${recommendation.type === 'digital_twin' ? 'text-white/80' : 
                      recommendation.type === 'airport' ? 'text-secondary' : 'text-success'}`}>
                      {recommendation.type === 'digital_twin' && (
                        <>
                          <TrendingUp className="w-3 h-3" />
                          <span>Projected: ${recommendation.projected_earnings}/day</span>
                        </>
                      )}
                      {recommendation.type === 'airport' && (
                        <>
                          <Clock className="w-3 h-3" />
                          <span>{recommendation.peak_time}</span>
                        </>
                      )}
                      {recommendation.type === 'wellbeing' && (
                        <>
                          <Target className="w-3 h-3" />
                          <span>Score: {recommendation.score}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Today's Stats</h2>
          <div className="grid grid-cols-2 gap-3">
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Rides</p>
              <p className="text-3xl font-bold text-foreground mt-1">{dashboardData.quick_stats.rides_today}</p>
              <p className="text-xs text-success mt-1">+3 from yesterday</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Rating</p>
              <div className="flex items-center gap-1 mt-1">
                <p className="text-3xl font-bold text-foreground">{dashboardData.quick_stats.rating}</p>
                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
              </div>
              <p className="text-xs text-muted-foreground mt-1">Excellent</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Acceptance</p>
              <p className="text-3xl font-bold text-foreground mt-1">{dashboardData.quick_stats.acceptance_rate}%</p>
              <p className="text-xs text-success mt-1">Above target</p>
            </Card>
            <Card className="p-4 bg-card border-border">
              <p className="text-sm text-muted-foreground">Avg/Hour</p>
              <p className="text-3xl font-bold text-secondary mt-1">${dashboardData.quick_stats.avg_per_hour}</p>
              <p className="text-xs text-secondary mt-1">Peak rate</p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
