import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Clock, Zap, Play, Pause, CheckCircle, Plus, Brain, TrendingUp, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { TimeBlock } from '../../types/enhanced-features';

const ENERGY_LEVELS = [
  { value: 'low', label: 'Low Energy', color: '#EF4444', icon: '🔴' },
  { value: 'medium', label: 'Medium Energy', color: '#F59E0B', icon: '🟡' },
  { value: 'high', label: 'High Energy', color: '#10B981', icon: '🟢' },
];

const HOURS = Array.from({ length: 24 }, (_, i) => {
  const hour = i;
  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return { value: hour, label: `${displayHour}:00 ${period}` };
});

export default function CalendarTimeBlocking() {
  const {
    timeBlocks,
    pillars,
    energyPatterns,
    smartSuggestions,
    addTimeBlock,
    updateTimeBlock,
    completeTimeBlock,
    deleteTimeBlock,
    updateEnergyPattern,
    getTodaysTimeBlocks,
    dismissSuggestion
  } = useEnhancedFeaturesStore();

  const [isCreateBlockOpen, setIsCreateBlockOpen] = useState(false);
  const [isEnergyTrackingOpen, setIsEnergyTrackingOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [activeBlock, setActiveBlock] = useState<TimeBlock | null>(null);

  // Form states
  const [blockTitle, setBlockTitle] = useState('');
  const [blockPillar, setBlockPillar] = useState('');
  const [blockStartTime, setBlockStartTime] = useState('');
  const [blockEndTime, setBlockEndTime] = useState('');
  const [blockEnergyLevel, setBlockEnergyLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [blockNotes, setBlockNotes] = useState('');

  const todaysBlocks = getTodaysTimeBlocks();
  const activeSuggestions = smartSuggestions.filter(s => !s.dismissed);

  // Energy tracking data
  const energyData = useMemo(() => {
    const data = Array.from({ length: 24 }, (_, hour) => {
      const patterns = energyPatterns.filter(p => p.hourOfDay === hour);
      const avgEnergy = patterns.length > 0 
        ? patterns.reduce((sum, p) => sum + p.averageEnergyLevel, 0) / patterns.length 
        : 5;
      
      return {
        hour: hour === 0 ? '12 AM' : hour === 12 ? '12 PM' : hour > 12 ? `${hour - 12} PM` : `${hour} AM`,
        energy: avgEnergy,
        sampleSize: patterns.reduce((sum, p) => sum + p.sampleSize, 0)
      };
    });
    return data;
  }, [energyPatterns]);

  // Pillar time allocation
  const pillarTimeData = useMemo(() => {
    const allocation = pillars.map(pillar => {
      const pillarBlocks = todaysBlocks.filter(block => block.pillarId === pillar.id);
      const totalTime = pillarBlocks.reduce((sum, block) => {
        const start = new Date(block.startTime);
        const end = new Date(block.endTime);
        return sum + (end.getTime() - start.getTime()) / (1000 * 60 * 60); // hours
      }, 0);

      return {
        name: pillar.name,
        planned: totalTime,
        target: pillar.weeklyTimeTarget / 7, // daily target
        color: pillar.color
      };
    });

    return allocation;
  }, [pillars, todaysBlocks]);

  const handleCreateBlock = () => {
    if (!blockTitle || !blockPillar || !blockStartTime || !blockEndTime) return;

    const startDate = new Date(selectedDate);
    const [startHour, startMinute] = blockStartTime.split(':').map(Number);
    startDate.setHours(startHour, startMinute, 0, 0);

    const endDate = new Date(selectedDate);
    const [endHour, endMinute] = blockEndTime.split(':').map(Number);
    endDate.setHours(endHour, endMinute, 0, 0);

    addTimeBlock({
      title: blockTitle,
      pillarId: blockPillar,
      taskIds: [],
      startTime: startDate,
      endTime: endDate,
      energyLevel: blockEnergyLevel,
      completed: false
    });

    // Reset form
    setBlockTitle('');
    setBlockPillar('');
    setBlockStartTime('');
    setBlockEndTime('');
    setBlockEnergyLevel('medium');
    setBlockNotes('');
    setIsCreateBlockOpen(false);
  };

  const handleStartBlock = (block: TimeBlock) => {
    setActiveBlock(block);
    updateTimeBlock(block.id, { actualStartTime: new Date() });
  };

  const handleCompleteBlock = (block: TimeBlock) => {
    completeTimeBlock(block.id, blockNotes);
    setActiveBlock(null);
    setBlockNotes('');
    
    // Update energy pattern
    const now = new Date();
    updateEnergyPattern(now.getHours(), now.getDay(), 
      block.energyLevel === 'high' ? 8 : block.energyLevel === 'medium' ? 5 : 3);
  };

  const getEnergyLevelColor = (level: 'low' | 'medium' | 'high') => {
    return ENERGY_LEVELS.find(e => e.value === level)?.color || '#B8BCC8';
  };

  const getOptimalEnergyTimes = () => {
    const sorted = energyData
      .filter(d => d.sampleSize > 0)
      .sort((a, b) => b.energy - a.energy)
      .slice(0, 3);
    
    return sorted.map(d => d.hour);
  };

  const optimalTimes = getOptimalEnergyTimes();

  return (
    <div className="space-y-6">
      {/* Smart Suggestions */}
      {activeSuggestions.length > 0 && (
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white border-l-4 border-l-[#F4D03F]">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-[#F4D03F]" />
              <span>Smart Scheduling Suggestions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeSuggestions.slice(0, 2).map((suggestion) => (
                <motion.div
                  key={suggestion.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium text-white">{suggestion.title}</div>
                    <div className="text-sm text-[#B8BCC8]">{suggestion.description}</div>
                    <Badge variant="outline" className="mt-1 text-xs border-[#F4D03F] text-[#F4D03F]">
                      {Math.round(suggestion.confidence * 100)}% confidence
                    </Badge>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => dismissSuggestion(suggestion.id)}
                    className="text-[#B8BCC8] hover:text-white"
                  >
                    Dismiss
                  </Button>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Today's Schedule */}
      <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-[#F4D03F]" />
              <span>Today's Schedule</span>
            </div>
            <div className="flex space-x-2">
              <Button
                size="sm"
                onClick={() => setIsEnergyTrackingOpen(true)}
                className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                variant="ghost"
              >
                <Zap className="w-4 h-4 mr-1" />
                Energy
              </Button>
              <Button
                size="sm"
                onClick={() => setIsCreateBlockOpen(true)}
                className="aurum-gradient text-[#0B0D14]"
              >
                <Plus className="w-4 h-4 mr-1" />
                Block Time
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {todaysBlocks.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-[#B8BCC8] mx-auto mb-4" />
              <p className="text-[#B8BCC8] mb-4">No time blocks scheduled for today</p>
              <Button
                onClick={() => setIsCreateBlockOpen(true)}
                className="aurum-gradient text-[#0B0D14]"
              >
                Schedule Your First Block
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {todaysBlocks
                .sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime())
                .map((block) => (
                  <motion.div
                    key={block.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-4 glassmorphism-panel rounded-lg border-l-4 ${
                      block.completed ? 'opacity-75' : ''
                    }`}
                    style={{ borderLeftColor: getEnergyLevelColor(block.energyLevel) }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-white">{block.title}</h3>
                          <Badge
                            variant="outline"
                            style={{ 
                              borderColor: getEnergyLevelColor(block.energyLevel),
                              color: getEnergyLevelColor(block.energyLevel)
                            }}
                          >
                            {ENERGY_LEVELS.find(e => e.value === block.energyLevel)?.icon} {block.energyLevel}
                          </Badge>
                          {block.completed && (
                            <Badge className="bg-green-500 text-white">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Completed
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-[#B8BCC8]">
                          <span>
                            {new Date(block.startTime).toLocaleTimeString('en-US', { 
                              hour: 'numeric', 
                              minute: '2-digit',
                              hour12: true 
                            })} - {new Date(block.endTime).toLocaleTimeString('en-US', { 
                              hour: 'numeric', 
                              minute: '2-digit',
                              hour12: true 
                            })}
                          </span>
                          <span>
                            {pillars.find(p => p.id === block.pillarId)?.name || 'Unknown Pillar'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {!block.completed && !activeBlock && (
                          <Button
                            size="sm"
                            onClick={() => handleStartBlock(block)}
                            className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                            variant="ghost"
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                        )}
                        {activeBlock?.id === block.id && (
                          <Button
                            size="sm"
                            onClick={() => handleCompleteBlock(block)}
                            className="bg-green-500 hover:bg-green-600 text-white"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                    
                    {block.notes && (
                      <div className="mt-3 p-2 bg-[rgba(244,208,63,0.1)] rounded text-sm text-[#B8BCC8]">
                        {block.notes}
                      </div>
                    )}
                  </motion.div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Energy Patterns */}
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-[#F4D03F]" />
              <span>Energy Patterns</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {energyData.filter(d => d.sampleSize > 0).length === 0 ? (
              <div className="text-center py-6">
                <AlertCircle className="w-8 h-8 text-[#B8BCC8] mx-auto mb-3" />
                <p className="text-[#B8BCC8] text-sm">
                  Complete some time blocks to see your energy patterns
                </p>
              </div>
            ) : (
              <>
                <div className="h-48 mb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={energyData.filter(d => d.sampleSize > 0)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                      <XAxis 
                        dataKey="hour" 
                        stroke="#B8BCC8" 
                        fontSize={11}
                      />
                      <YAxis 
                        stroke="#B8BCC8" 
                        fontSize={11}
                        domain={[0, 10]}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1A1D29', 
                          border: '1px solid rgba(244,208,63,0.2)',
                          borderRadius: '8px',
                          color: '#FFFFFF'
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="energy" 
                        stroke="#F4D03F" 
                        strokeWidth={2}
                        dot={{ fill: '#F4D03F', strokeWidth: 2, r: 3 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                
                {optimalTimes.length > 0 && (
                  <div className="glassmorphism-panel p-3 rounded-lg">
                    <div className="text-sm font-medium text-white mb-2">Optimal Focus Times</div>
                    <div className="flex flex-wrap gap-2">
                      {optimalTimes.map((time) => (
                        <Badge key={time} className="aurum-gradient text-[#0B0D14]">
                          {time}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Pillar Time Allocation */}
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-[#F4D03F]" />
              <span>Today's Pillar Allocation</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {pillarTimeData.filter(p => p.planned > 0).length === 0 ? (
              <div className="text-center py-6">
                <Clock className="w-8 h-8 text-[#B8BCC8] mx-auto mb-3" />
                <p className="text-[#B8BCC8] text-sm">
                  No time allocated to pillars today
                </p>
              </div>
            ) : (
              <>
                <div className="h-48 mb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={pillarTimeData.filter(p => p.planned > 0)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                      <XAxis 
                        dataKey="name" 
                        stroke="#B8BCC8" 
                        fontSize={11}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis 
                        stroke="#B8BCC8" 
                        fontSize={11}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1A1D29', 
                          border: '1px solid rgba(244,208,63,0.2)',
                          borderRadius: '8px',
                          color: '#FFFFFF'
                        }}
                      />
                      <Bar 
                        dataKey="planned" 
                        fill="#F4D03F" 
                        radius={[4, 4, 0, 0]}
                        name="Planned Hours"
                      />
                      <Bar 
                        dataKey="target" 
                        fill="rgba(244,208,63,0.3)" 
                        radius={[4, 4, 0, 0]}
                        name="Daily Target"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="space-y-2">
                  {pillarTimeData
                    .filter(p => p.planned > 0)
                    .map((pillar) => (
                      <div key={pillar.name} className="flex items-center justify-between text-sm">
                        <span className="text-[#B8BCC8]">{pillar.name}</span>
                        <span className="text-white">
                          {pillar.planned.toFixed(1)}h / {pillar.target.toFixed(1)}h
                        </span>
                      </div>
                    ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Time Block Modal */}
      <Dialog open={isCreateBlockOpen} onOpenChange={setIsCreateBlockOpen}>
        <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-[#F4D03F]" />
              <span>Create Time Block</span>
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#B8BCC8] mb-2">
                Block Title
              </label>
              <Input
                value={blockTitle}
                onChange={(e) => setBlockTitle(e.target.value)}
                placeholder="e.g., Deep work on project..."
                className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#B8BCC8] mb-2">
                Pillar
              </label>
              <Select value={blockPillar} onValueChange={setBlockPillar}>
                <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue placeholder="Select a pillar" />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                  {pillars.map((pillar) => (
                    <SelectItem key={pillar.id} value={pillar.id}>
                      {pillar.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[#B8BCC8] mb-2">
                  Start Time
                </label>
                <Input
                  type="time"
                  value={blockStartTime}
                  onChange={(e) => setBlockStartTime(e.target.value)}
                  className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white focus:border-[#F4D03F]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#B8BCC8] mb-2">
                  End Time
                </label>
                <Input
                  type="time"
                  value={blockEndTime}
                  onChange={(e) => setBlockEndTime(e.target.value)}
                  className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white focus:border-[#F4D03F]"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#B8BCC8] mb-2">
                Required Energy Level
              </label>
              <Select value={blockEnergyLevel} onValueChange={(value: any) => setBlockEnergyLevel(value)}>
                <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                  {ENERGY_LEVELS.map((level) => (
                    <SelectItem key={level.value} value={level.value}>
                      <div className="flex items-center space-x-2">
                        <span>{level.icon}</span>
                        <span>{level.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setIsCreateBlockOpen(false)}
                className="border-[rgba(244,208,63,0.3)] text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateBlock}
                disabled={!blockTitle || !blockPillar || !blockStartTime || !blockEndTime}
                className="aurum-gradient text-[#0B0D14]"
              >
                Create Block
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Energy Tracking Modal */}
      <Dialog open={isEnergyTrackingOpen} onOpenChange={setIsEnergyTrackingOpen}>
        <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-[#F4D03F]" />
              <span>Energy Tracking & Optimization</span>
            </DialogTitle>
          </DialogHeader>

          <Tabs defaultValue="patterns" className="w-full">
            <TabsList className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] mb-6">
              <TabsTrigger value="patterns" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                Patterns
              </TabsTrigger>
              <TabsTrigger value="optimization" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                Optimization
              </TabsTrigger>
            </TabsList>

            <TabsContent value="patterns">
              <div className="space-y-6">
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={energyData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                      <XAxis dataKey="hour" stroke="#B8BCC8" />
                      <YAxis stroke="#B8BCC8" domain={[0, 10]} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1A1D29', 
                          border: '1px solid rgba(244,208,63,0.2)',
                          borderRadius: '8px',
                          color: '#FFFFFF'
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="energy" 
                        stroke="#F4D03F" 
                        strokeWidth={3}
                        dot={{ fill: '#F4D03F', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  {ENERGY_LEVELS.map((level) => (
                    <div key={level.value} className="glassmorphism-panel p-4 rounded-lg text-center">
                      <div className="text-2xl mb-2">{level.icon}</div>
                      <div className="font-medium text-white">{level.label}</div>
                      <div className="text-sm text-[#B8BCC8] mt-1">
                        Best for: {level.value === 'high' ? 'Creative work, problem solving' : 
                                  level.value === 'medium' ? 'Routine tasks, meetings' : 
                                  'Administrative work, planning'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="optimization">
              <div className="space-y-6">
                {optimalTimes.length > 0 && (
                  <div className="glassmorphism-panel p-4 rounded-lg">
                    <h3 className="font-semibold text-white mb-3">Recommended Schedule Adjustments</h3>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <TrendingUp className="w-5 h-5 text-green-400 mt-0.5" />
                        <div>
                          <div className="text-white">Schedule high-energy tasks during peak hours</div>
                          <div className="text-sm text-[#B8BCC8]">
                            Your peak energy times: {optimalTimes.join(', ')}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Clock className="w-5 h-5 text-[#F4D03F] mt-0.5" />
                        <div>
                          <div className="text-white">Reserve low-energy periods for admin work</div>
                          <div className="text-sm text-[#B8BCC8]">
                            Use energy dips for emails, planning, and routine tasks
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div className="text-center text-[#B8BCC8]">
                  <p>Complete more time blocks to get personalized energy optimization suggestions</p>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
}