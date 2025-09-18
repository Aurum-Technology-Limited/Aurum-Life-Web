import { useState } from 'react';
import { MessageCircle, Bug, Lightbulb, MessageSquare, Star, Upload, X, Filter, ThumbsUp, ExternalLink, Twitter, Linkedin } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Checkbox } from '../ui/checkbox';
import { Badge } from '../ui/badge';

export default function Feedback() {
  const [rating, setRating] = useState(0);
  const [feedbackHistory] = useState([
    {
      id: 1,
      type: 'Feature Request',
      title: 'Dark mode for calendar view',
      preview: 'Would love to see a dark mode option for the calendar component...',
      status: 'Implemented',
      date: '2024-01-15',
      votes: 23
    },
    {
      id: 2,
      type: 'Bug Report',
      title: 'Task sync issue',
      preview: 'Tasks are not syncing properly between devices...',
      status: 'In Review',
      date: '2024-01-10',
      votes: 0
    },
    {
      id: 3,
      type: 'General Feedback',
      title: 'Love the AI insights!',
      preview: 'The AI recommendations have really helped me stay on track...',
      status: 'Closed',
      date: '2024-01-05',
      votes: 0
    }
  ]);

  const [communityRequests] = useState([
    {
      id: 1,
      title: 'Pomodoro Timer Integration',
      description: 'Built-in pomodoro timer with break reminders and productivity tracking',
      votes: 145,
      status: 'Planned'
    },
    {
      id: 2,
      title: 'Team Collaboration Features',
      description: 'Share goals and projects with team members for collaborative planning',
      votes: 89,
      status: 'Under Review'
    },
    {
      id: 3,
      title: 'Voice Notes for Journal',
      description: 'Record voice memos that automatically transcribe to journal entries',
      votes: 67,
      status: 'Considering'
    },
    {
      id: 4,
      title: 'Calendar Integration',
      description: 'Two-way sync with Google Calendar, Outlook, and Apple Calendar',
      votes: 134,
      status: 'In Development'
    }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Implemented': return 'bg-[#10B981] text-white';
      case 'In Review': return 'bg-[#F59E0B] text-white';
      case 'Planned': return 'bg-[#3B82F6] text-white';
      case 'In Development': return 'bg-[#F4D03F] text-[#0B0D14]';
      case 'Under Review': return 'bg-[#F59E0B] text-white';
      case 'Considering': return 'bg-[#B8BCC8] text-[#0B0D14]';
      default: return 'bg-[#6B7280] text-white';
    }
  };

  const StarRating = ({ value, onChange, size = 5 }) => {
    return (
      <div className="flex space-x-1">
        {[...Array(size)].map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onChange(i + 1)}
            className={`w-8 h-8 ${i < value ? 'text-[#F4D03F]' : 'text-[#6B7280]'} hover:text-[#F4D03F] transition-colors`}
          >
            <Star className={`w-6 h-6 ${i < value ? 'fill-current' : ''}`} />
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center space-x-3">
        <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
          <MessageCircle className="w-6 h-6 text-[#0B0D14]" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Feedback</h1>
          <p className="text-[#B8BCC8]">Help us improve your Aurum Life experience</p>
        </div>
      </div>

      {/* Feedback Tabs */}
      <Card className="glassmorphism-card border-0">
        <CardContent className="p-0">
          <Tabs defaultValue="bug-report" className="w-full">
            <CardHeader>
              <TabsList className="grid w-full grid-cols-4 bg-[#1A1D29] border border-[rgba(244,208,63,0.2)]">
                <TabsTrigger value="bug-report" className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                  <Bug className="w-4 h-4 mr-2" />
                  Bug Report
                </TabsTrigger>
                <TabsTrigger value="feature-request" className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Feature Request
                </TabsTrigger>
                <TabsTrigger value="general-feedback" className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  General Feedback
                </TabsTrigger>
                <TabsTrigger value="app-review" className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                  <Star className="w-4 h-4 mr-2" />
                  App Review
                </TabsTrigger>
              </TabsList>
            </CardHeader>

            {/* Bug Report Tab */}
            <TabsContent value="bug-report" className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="issue-category" className="text-white">Issue Category</Label>
                  <Select>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectItem value="ui">UI/Interface</SelectItem>
                      <SelectItem value="performance">Performance</SelectItem>
                      <SelectItem value="sync">Synchronization</SelectItem>
                      <SelectItem value="crash">App Crash</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white">Severity Level</Label>
                  <RadioGroup defaultValue="medium" className="flex space-x-4 mt-2">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="low" id="low" />
                      <Label htmlFor="low" className="text-[#B8BCC8]">Low</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="medium" id="medium" />
                      <Label htmlFor="medium" className="text-[#B8BCC8]">Medium</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="high" id="high" />
                      <Label htmlFor="high" className="text-[#B8BCC8]">High</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="critical" id="critical" />
                      <Label htmlFor="critical" className="text-[#B8BCC8]">Critical</Label>
                    </div>
                  </RadioGroup>
                </div>
              </div>

              <div>
                <Label htmlFor="what-happened" className="text-white">What happened?</Label>
                <Textarea
                  id="what-happened"
                  placeholder="Describe the bug or issue you encountered..."
                  className="mt-2 min-h-[120px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label htmlFor="steps-to-reproduce" className="text-white">Steps to reproduce</Label>
                <Textarea
                  id="steps-to-reproduce"
                  placeholder="1. Go to..."
                  className="mt-2 min-h-[100px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label htmlFor="expected-behavior" className="text-white">Expected behavior</Label>
                <Textarea
                  id="expected-behavior"
                  placeholder="What did you expect to happen?"
                  className="mt-2 min-h-[80px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label className="text-white">Screenshot (optional)</Label>
                <div className="mt-2 border-2 border-dashed border-[rgba(244,208,63,0.3)] rounded-lg p-8 text-center">
                  <Upload className="w-8 h-8 text-[#F4D03F] mx-auto mb-2" />
                  <p className="text-[#B8BCC8]">Drag and drop screenshot here, or click to upload</p>
                  <Button variant="outline" className="mt-2 border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                    Upload Screenshot
                  </Button>
                </div>
              </div>

              <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Submit Bug Report
              </Button>
            </TabsContent>

            {/* Feature Request Tab */}
            <TabsContent value="feature-request" className="p-6 space-y-6">
              <div>
                <Label htmlFor="feature-category" className="text-white">Feature Category</Label>
                <Select>
                  <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectItem value="ai">AI Features</SelectItem>
                    <SelectItem value="analytics">Analytics</SelectItem>
                    <SelectItem value="goals">Goals & Planning</SelectItem>
                    <SelectItem value="tasks">Task Management</SelectItem>
                    <SelectItem value="ui">User Interface</SelectItem>
                    <SelectItem value="integration">Integrations</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="feature-description" className="text-white">Describe your idea</Label>
                <Textarea
                  id="feature-description"
                  placeholder="What feature would you like to see added?"
                  className="mt-2 min-h-[120px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label htmlFor="feature-usefulness" className="text-white">Why would this be useful?</Label>
                <Textarea
                  id="feature-usefulness"
                  placeholder="How would this feature help you achieve your goals?"
                  className="mt-2 min-h-[100px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label className="text-white">Priority Level</Label>
                <div className="mt-2">
                  <StarRating value={rating} onChange={setRating} />
                </div>
              </div>

              <div>
                <Label className="text-white">Attach mockup/sketch (optional)</Label>
                <div className="mt-2 border-2 border-dashed border-[rgba(244,208,63,0.3)] rounded-lg p-6 text-center">
                  <Upload className="w-6 h-6 text-[#F4D03F] mx-auto mb-2" />
                  <p className="text-[#B8BCC8] text-sm">Upload design files or sketches</p>
                  <Button variant="outline" size="sm" className="mt-2 border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                    Choose File
                  </Button>
                </div>
              </div>

              <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Submit Feature Request
              </Button>
            </TabsContent>

            {/* General Feedback Tab */}
            <TabsContent value="general-feedback" className="p-6 space-y-6">
              <div>
                <Label className="text-white">How would you rate Aurum Life?</Label>
                <div className="mt-2">
                  <StarRating value={rating} onChange={setRating} />
                </div>
              </div>

              <div>
                <Label htmlFor="love-most" className="text-white">What do you love most?</Label>
                <Textarea
                  id="love-most"
                  placeholder="Tell us what you enjoy about using Aurum Life..."
                  className="mt-2 min-h-[100px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label htmlFor="could-improve" className="text-white">What could be improved?</Label>
                <Textarea
                  id="could-improve"
                  placeholder="Share your suggestions for improvement..."
                  className="mt-2 min-h-[100px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div>
                <Label htmlFor="additional-comments" className="text-white">Additional comments</Label>
                <Textarea
                  id="additional-comments"
                  placeholder="Any other thoughts or feedback..."
                  className="mt-2 min-h-[80px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox id="contact-permission" />
                <Label htmlFor="contact-permission" className="text-[#B8BCC8]">
                  It's okay to contact me about this feedback
                </Label>
              </div>

              <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Submit Feedback
              </Button>
            </TabsContent>

            {/* App Review Tab */}
            <TabsContent value="app-review" className="p-6 space-y-6">
              <div className="text-center space-y-4">
                <div>
                  <h3 className="text-xl font-medium text-white mb-2">Rate Aurum Life</h3>
                  <div className="flex justify-center">
                    <StarRating value={rating} onChange={setRating} />
                  </div>
                </div>

                <div>
                  <Label htmlFor="review-text" className="text-white">Write a review</Label>
                  <Textarea
                    id="review-text"
                    placeholder="Share your experience with other users..."
                    className="mt-2 min-h-[120px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  />
                </div>

                <div className="space-y-3">
                  <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Share on App Store
                  </Button>

                  <div className="grid grid-cols-2 gap-3">
                    <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                      <Twitter className="w-4 h-4 mr-2" />
                      Share on Twitter
                    </Button>
                    <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                      <Linkedin className="w-4 h-4 mr-2" />
                      Share on LinkedIn
                    </Button>
                  </div>

                  <Button variant="ghost" className="text-[#B8BCC8] hover:text-[#F4D03F]">
                    Maybe Later
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Previous Feedback Section */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white">Your Feedback History</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Track the status of your submissions
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {feedbackHistory.map((feedback) => (
              <div key={feedback.id} className="glassmorphism-panel p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Badge variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                        {feedback.type}
                      </Badge>
                      <Badge className={getStatusColor(feedback.status)}>
                        {feedback.status}
                      </Badge>
                      <span className="text-[#6B7280] text-sm">{feedback.date}</span>
                    </div>
                    <h4 className="text-white font-medium mb-1">{feedback.title}</h4>
                    <p className="text-[#B8BCC8] text-sm">{feedback.preview}</p>
                  </div>
                  <Button variant="ghost" size="sm" className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]">
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Community Section */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Feature Requests from Community</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Vote on features you'd like to see implemented
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {communityRequests.map((request) => (
              <div key={request.id} className="glassmorphism-panel p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="text-white font-medium mb-1">{request.title}</h4>
                    <p className="text-[#B8BCC8] text-sm mb-2">{request.description}</p>
                    <Badge className={getStatusColor(request.status)}>
                      {request.status}
                    </Badge>
                  </div>
                  <div className="text-center ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                    >
                      <ThumbsUp className="w-4 h-4 mr-1" />
                      {request.votes}
                    </Button>
                  </div>
                </div>
                <Button size="sm" className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                  Vote
                </Button>
              </div>
            ))}
          </div>
          
          <div className="mt-6 text-center">
            <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              Submit Your Own Request
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}