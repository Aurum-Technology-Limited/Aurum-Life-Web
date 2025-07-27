import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Check, AlertCircle, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { todayService } from '../services/api';

export default function TodayMVP() {
  const queryClient = useQueryClient();
  const [morningIntention, setMorningIntention] = useState('');
  const [eveningReflection, setEveningReflection] = useState('');
  const [isReflectionMode, setIsReflectionMode] = useState(false);

  // Check if it's evening (after 6 PM)
  useEffect(() => {
    const hour = new Date().getHours();
    setIsReflectionMode(hour >= 18);
  }, []);

  // Fetch today's tasks
  const { data: todayData, isLoading } = useQuery({
    queryKey: ['today-tasks'],
    queryFn: todayService.getTodayTasks,
    refetchInterval: 60000, // Refresh every minute
  });

  // Load saved intentions/reflections
  useEffect(() => {
    const savedIntention = localStorage.getItem(`intention-${format(new Date(), 'yyyy-MM-dd')}`);
    const savedReflection = localStorage.getItem(`reflection-${format(new Date(), 'yyyy-MM-dd')}`);
    
    if (savedIntention) setMorningIntention(savedIntention);
    if (savedReflection) setEveningReflection(savedReflection);
  }, []);

  // Toggle task completion
  const toggleTaskMutation = useMutation({
    mutationFn: ({ taskId, completed }) => 
      todayService.updateTask(taskId, { completed }),
    onSuccess: () => {
      queryClient.invalidateQueries(['today-tasks']);
      toast.success('Task updated');
    },
    onError: () => {
      toast.error('Failed to update task');
    },
  });

  // Save intention
  const saveIntention = () => {
    const today = format(new Date(), 'yyyy-MM-dd');
    localStorage.setItem(`intention-${today}`, morningIntention);
    toast.success('Morning intention saved');
  };

  // Save reflection
  const saveReflection = () => {
    const today = format(new Date(), 'yyyy-MM-dd');
    localStorage.setItem(`reflection-${today}`, eveningReflection);
    toast.success('Evening reflection saved');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const tasks = todayData?.tasks || [];
  const completedCount = tasks.filter(t => t.completed).length;
  const completionRate = tasks.length > 0 ? (completedCount / tasks.length) * 100 : 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Today</h1>
          <p className="text-muted-foreground">{format(new Date(), 'EEEE, MMMM d, yyyy')}</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{completedCount}/{tasks.length}</div>
          <p className="text-sm text-muted-foreground">Tasks completed</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-secondary rounded-full h-2">
        <div 
          className="bg-primary h-2 rounded-full transition-all duration-300"
          style={{ width: `${completionRate}%` }}
        />
      </div>

      {/* Morning Intention */}
      {!isReflectionMode && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Morning Intention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What's your main focus for today?"
              value={morningIntention}
              onChange={(e) => setMorningIntention(e.target.value)}
              className="min-h-[100px]"
            />
            <Button 
              onClick={saveIntention}
              className="mt-4"
              disabled={!morningIntention.trim()}
            >
              Save Intention
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Task List */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          {tasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No tasks scheduled for today</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <div 
                  key={task.id}
                  className={`flex items-start gap-3 p-3 rounded-lg border ${
                    task.completed ? 'bg-muted opacity-60' : 'bg-background'
                  }`}
                >
                  <Checkbox
                    checked={task.completed}
                    onCheckedChange={(checked) => 
                      toggleTaskMutation.mutate({ 
                        taskId: task.id, 
                        completed: checked 
                      })
                    }
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className={`font-medium ${task.completed ? 'line-through' : ''}`}>
                      {task.name}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {task.project_name} • {task.area_name}
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      {task.priority === 'high' && (
                        <Badge variant="destructive" className="text-xs">High Priority</Badge>
                      )}
                      {task.due_date && (
                        <Badge variant="outline" className="text-xs">
                          Due {format(new Date(task.due_date), 'h:mm a')}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Evening Reflection */}
      {isReflectionMode && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              Evening Reflection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="How did today go? What did you learn?"
              value={eveningReflection}
              onChange={(e) => setEveningReflection(e.target.value)}
              className="min-h-[100px]"
            />
            <Button 
              onClick={saveReflection}
              className="mt-4"
              disabled={!eveningReflection.trim()}
            >
              Save Reflection
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}