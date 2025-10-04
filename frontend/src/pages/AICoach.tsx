import React, { useState, useEffect } from 'react';
import { Brain, Zap, TrendingUp, Clock, Target, Star, Users, BarChart3, Calendar, MapPin, Trophy, AlertCircle, CheckCircle2, RefreshCw, Menu } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { uberDriverAPI, type EnhancedDigitalTwinProfile, type OptimizationScenario, type DriverListItem, type DriverComparison } from '@/lib/api';

const AICoach: React.FC = () => {
  const [profile, setProfile] = useState<EnhancedDigitalTwinProfile | null>(null);
  const [scenarios, setScenarios] = useState<OptimizationScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [currentPerformance, setCurrentPerformance] = useState<any>(null);
  const [behavioralProfile, setBehavioralProfile] = useState<any>(null);
  const [keyInsights, setKeyInsights] = useState<string[]>([]);
  const [availableDrivers, setAvailableDrivers] = useState<DriverListItem[]>([]);
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([]);
  const [driverComparison, setDriverComparison] = useState<DriverComparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [currentDriverId, setCurrentDriverId] = useState('E10156');

  useEffect(() => {
    loadDigitalTwinData();
    loadAvailableDrivers();
  }, [currentDriverId]);

  const loadDigitalTwinData = async () => {
    try {
      setLoading(true);
      
      const [profileData, optimizationData] = await Promise.all([
        uberDriverAPI.getDigitalTwinProfile(currentDriverId),
        uberDriverAPI.optimizeSchedule(currentDriverId)
      ]);

      setProfile(profileData.profile);
      setScenarios(optimizationData.scenarios);
      setSelectedScenario(optimizationData.best_scenario);
      setCurrentPerformance(optimizationData.current_performance);
      setBehavioralProfile(optimizationData.behavioral_profile);
      setKeyInsights(optimizationData.key_insights);
    } catch (error) {
      console.error('Error loading Digital Twin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableDrivers = async () => {
    try {
      const driversData = await uberDriverAPI.getAvailableDrivers();
      setAvailableDrivers(driversData.top_drivers);
    } catch (error) {
      console.error('Error loading available drivers:', error);
    }
  };

  const handleCompareDrivers = async () => {
    if (selectedDrivers.length < 2) return;
    
    try {
      const comparison = await uberDriverAPI.compareDrivers(selectedDrivers);
      setDriverComparison(comparison.drivers);
    } catch (error) {
      console.error('Error comparing drivers:', error);
    }
  };

  const applyOptimization = (scenarioName: string) => {
    const scenario = scenarios.find(s => s.name === scenarioName);
    if (!scenario) return;

    alert(`🎯 Applying "${scenario.display_name}" Strategy!\n\n` +
          `📈 Projected Earnings: €${scenario.projected_earnings}/week\n` +
          `⚡ Improvement: +${scenario.improvement}%\n` +
          `⏰ Weekly Hours: ${scenario.weekly_hours}h\n` +
          `🎯 Confidence: ${scenario.confidence}\n\n` +
          `Your Digital Twin will guide you through this optimization!`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-bg pb-24 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin h-8 w-8 text-primary mx-auto mb-2" />
          <span className="text-muted-foreground">AI is learning your driving patterns...</span>
        </div>
      </div>
    );
  }

  const getScenarioIcon = (scenarioName: string) => {
    const name = scenarioName.toLowerCase();
    if (name.includes('early')) return <Clock className="w-4 h-4" />;
    if (name.includes('surge')) return <Zap className="w-4 h-4" />;
    if (name.includes('weekend')) return <Target className="w-4 h-4" />;
    if (name.includes('consistent')) return <BarChart3 className="w-4 h-4" />;
    return <TrendingUp className="w-4 h-4" />;
  };

  const getScenarioColor = (improvement: number) => {
    if (improvement >= 500) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (improvement >= 250) return 'bg-green-100 text-green-800 border-green-200';
    if (improvement >= 100) return 'bg-blue-100 text-blue-800 border-blue-200';
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  };

  const formatSchedule = (schedule: Record<string, string>) => {
    return Object.entries(schedule).map(([day, times]) => (
      <div key={day} className="flex justify-between text-sm">
        <span className="font-medium text-foreground">{day}:</span>
        <span className="text-muted-foreground">{times}</span>
      </div>
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-bg pb-24">
      <div className="max-w-md mx-auto p-4 space-y-4">
        {/* Enhanced Header */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Optimization</h1>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={currentDriverId} onValueChange={setCurrentDriverId}>
              <SelectTrigger className="w-20 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availableDrivers.slice(0, 5).map(driver => (
                  <SelectItem key={driver.driver_id} value={driver.driver_id} className="text-xs">
                    {driver.driver_id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-muted text-xs">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="compare">Compare</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4 mt-4">
            {/* Current vs Optimized Performance */}
            {currentPerformance && (
              <div className="space-y-4">
                <Card className="bg-card border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-sm">
                      <AlertCircle className="w-4 h-4 text-orange-500" />
                      <span>Current Performance</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground text-sm">Weekly Earnings</span>
                      <span className="text-lg font-bold text-foreground">€{currentPerformance.weekly_earnings}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground text-sm">Weekly Hours</span>
                      <span className="text-sm font-semibold text-foreground">{currentPerformance.weekly_hours}h</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground text-sm">Efficiency Score</span>
                      <span className="text-sm font-semibold text-orange-600">{currentPerformance.efficiency_score}%</span>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-ai border-primary/50 shadow-glow-ai">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-sm text-white">
                      <CheckCircle2 className="w-4 h-4 text-white" />
                      <span>AI Optimized Potential</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {scenarios.length > 0 && (
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-white/70 text-sm">Best Strategy</span>
                          <Badge className="bg-white/20 text-white text-xs">
                            {selectedScenario.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-white/70 text-sm">Projected Earnings</span>
                          <span className="text-lg font-bold text-white">
                            €{scenarios.find(s => s.name === selectedScenario)?.projected_earnings || 0}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-white/70 text-sm">Improvement</span>
                          <span className="text-sm font-semibold text-white">
                            +{scenarios.find(s => s.name === selectedScenario)?.improvement || 0}%
                          </span>
                        </div>
                        <Button 
                          onClick={() => applyOptimization(selectedScenario)} 
                          className="w-full bg-white text-primary hover:bg-white/90 mt-3"
                        >
                          <Target className="w-3 h-3 mr-1" />
                          Apply This Strategy
                        </Button>
                      </>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Key Insights */}
            {keyInsights.length > 0 && (
              <Card className="bg-card border-border">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center space-x-2 text-sm">
                    <Trophy className="w-4 h-4 text-yellow-500" />
                    <span>AI Key Insights</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {keyInsights.slice(0, 3).map((insight, index) => (
                      <div key={index} className="flex items-start space-x-2 p-2 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-xs text-blue-800 dark:text-blue-200">{insight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Scenarios Tab */}
          <TabsContent value="scenarios" className="space-y-4 mt-4">
            {scenarios.map((scenario, index) => (
              <Card key={index} className={`${
                scenario.is_recommended ? 'border-green-500 bg-green-50/50 dark:bg-green-950/20' : 
                selectedScenario === scenario.name ? 'border-primary bg-blue-50/50 dark:bg-blue-950/20' : 
                'bg-card border-border'
              } cursor-pointer transition-all`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getScenarioIcon(scenario.name)}
                      <div>
                        <h3 className="font-semibold text-foreground text-sm">{scenario.display_name}</h3>
                        <Badge className={`${getScenarioColor(scenario.improvement)} text-xs`} variant="outline">
                          +{scenario.improvement.toFixed(0)}%
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-green-600">€{scenario.projected_earnings}</div>
                      <div className="text-xs text-muted-foreground">{scenario.weekly_hours}h/week</div>
                    </div>
                  </div>
                  
                  <p className="text-xs text-muted-foreground mb-3">{scenario.description}</p>
                  
                  <div className="space-y-2 mb-3">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">Feasibility</span>
                        <span className="text-muted-foreground">{Math.round(scenario.feasibility * 100)}%</span>
                      </div>
                      <Progress value={scenario.feasibility * 100} className="h-1" />
                    </div>
                  </div>

                  {/* Schedule Details */}
                  {Object.keys(scenario.schedule).length > 0 && (
                    <div className="mt-3 p-2 bg-muted/50 rounded-lg">
                      <div className="text-xs font-medium text-foreground mb-1">📅 Schedule:</div>
                      <div className="space-y-0.5 text-xs">
                        {Object.entries(scenario.schedule).slice(0, 3).map(([day, times]) => (
                          <div key={day} className="flex justify-between">
                            <span className="font-medium text-foreground">{day}:</span>
                            <span className="text-muted-foreground">{times}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2 mt-3">
                    <Button 
                      onClick={() => setSelectedScenario(scenario.name)}
                      variant={selectedScenario === scenario.name ? "default" : "outline"}
                      size="sm"
                      className="flex-1 text-xs"
                    >
                      Select
                    </Button>
                    <Button 
                      onClick={() => applyOptimization(scenario.name)}
                      variant="default" 
                      size="sm"
                      className="flex-1 bg-green-600 hover:bg-green-700 text-xs"
                    >
                      Apply
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-4 mt-4">
            {profile && behavioralProfile && (
              <>
                {/* Behavioral Profile */}
                <Card className="bg-card border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-sm">
                      <BarChart3 className="w-4 h-4 text-blue-500" />
                      <span>Behavioral Profile</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="text-xs font-medium text-foreground">Peak Hours: </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {behavioralProfile.preferred_hours.slice(0, 5).map((hour: number) => (
                          <Badge key={hour} variant="outline" className="text-xs px-1 py-0">
                            {hour}:00
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-xs font-medium text-foreground">Peak Days: </span>
                      <span className="text-xs text-muted-foreground">{behavioralProfile.peak_days.join(', ')}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-3">
                      <div className="text-center p-2 bg-blue-50 dark:bg-blue-950/20 rounded text-xs">
                        <div className="font-bold text-blue-600">€{behavioralProfile.avg_earnings_per_hour}</div>
                        <div className="text-muted-foreground">Avg/Hour</div>
                      </div>
                      <div className="text-center p-2 bg-purple-50 dark:bg-purple-950/20 rounded text-xs">
                        <div className="font-bold text-purple-600">{Math.round(behavioralProfile.consistency_score * 100)}%</div>
                        <div className="text-muted-foreground">Consistency</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Ride Statistics */}
                <Card className="bg-card border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-sm">
                      <MapPin className="w-4 h-4 text-green-500" />
                      <span>Ride Statistics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Total Rides</span>
                      <span className="font-semibold text-foreground">{profile.ride_statistics.total_rides}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Busiest Hour</span>
                      <span className="font-semibold text-foreground">{profile.ride_statistics.busiest_hour}</span>
                    </div>
                    <div className="mt-2 p-2 bg-muted/50 rounded-lg">
                      <div className="text-xs font-medium text-foreground mb-1">Earnings per Minute:</div>
                      <div className="text-xs space-y-1">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">All rides:</span>
                          <span className="text-foreground">€{profile.ride_statistics.earnings_per_minute_all}</span>
                        </div>
                        <div className="flex justify-between text-green-600">
                          <span>Short rides (&lt;15min):</span>
                          <span>€{profile.ride_statistics.earnings_per_minute_short}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Weekly Breakdown */}
                <Card className="bg-card border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-sm">
                      <Calendar className="w-4 h-4 text-purple-500" />
                      <span>Weekly Distribution</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-7 gap-1">
                      {Object.entries(profile.weekly_breakdown).map(([day, rides]) => (
                        <div key={day} className="text-center p-1 bg-muted/30 rounded text-xs">
                          <div className="font-medium text-foreground">{day.slice(0, 3)}</div>
                          <div className="text-sm font-bold text-blue-600">{rides}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Compare Tab */}
          <TabsContent value="compare" className="space-y-4 mt-4">
            <Card className="bg-card border-border">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2 text-sm">
                  <Users className="w-4 h-4 text-indigo-500" />
                  <span>Driver Comparison</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-medium text-foreground mb-2 block">Select Drivers:</label>
                    <div className="grid grid-cols-2 gap-2">
                      {availableDrivers.slice(0, 4).map(driver => (
                        <label key={driver.driver_id} className="flex items-center space-x-1 p-2 border rounded cursor-pointer hover:bg-muted/20 text-xs">
                          <input 
                            type="checkbox" 
                            className="w-3 h-3"
                            checked={selectedDrivers.includes(driver.driver_id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDrivers(prev => [...prev, driver.driver_id]);
                              } else {
                                setSelectedDrivers(prev => prev.filter(id => id !== driver.driver_id));
                              }
                            }}
                          />
                          <span className="text-foreground">{driver.driver_id}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleCompareDrivers} 
                    disabled={selectedDrivers.length < 2}
                    className="w-full text-xs"
                  >
                    <Users className="w-3 h-3 mr-1" />
                    Compare Drivers
                  </Button>

                  {driverComparison.length > 0 && (
                    <div className="space-y-3">
                      {driverComparison.map((driver, index) => (
                        <div key={index} className="p-3 border rounded-lg bg-muted/20">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-bold text-sm text-foreground">{driver.driver_id}</h3>
                            <Badge className="bg-blue-100 text-blue-800 text-xs">
                              {driver.best_strategy.replace('_', ' ').toUpperCase()}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="text-center p-1 bg-card rounded">
                              <div className="font-bold text-foreground">€{driver.current_weekly}</div>
                              <div className="text-muted-foreground">Current</div>
                            </div>
                            <div className="text-center p-1 bg-green-50 dark:bg-green-950/20 rounded">
                              <div className="font-bold text-green-600">€{driver.optimized_weekly}</div>
                              <div className="text-muted-foreground">Optimized</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AICoach;
