import { useState } from 'react';
import { HelpCircle, MessageCircle, Bug, FileText, Video, Book, Mail, ExternalLink, Search, ChevronRight, Send, CheckCircle2, AlertCircle, Star, ThumbsUp, ThumbsDown, Target, Cloud, Brain, Zap } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Textarea } from '../../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Badge } from '../../ui/badge';
import { Alert, AlertDescription } from '../../ui/alert';
import { Switch } from '../../ui/switch';
import { motion } from 'motion/react';
import { useForm, Controller } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { supportRequestSchema, feedbackSchema, type SupportRequestData, type FeedbackData } from '../../../schemas/settings';
import { useAppStore } from '../../../stores/basicAppStore';
import { toast } from 'sonner@2.0.3';

export default function HelpSettings() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'help' | 'support' | 'feedback'>('help');
  const [isSubmittingSupport, setIsSubmittingSupport] = useState(false);
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);

  const addNotification = useAppStore(state => state.addNotification);

  // Support form
  const supportForm = useForm<SupportRequestData>({
    resolver: zodResolver(supportRequestSchema),
    defaultValues: {
      category: 'general',
      priority: 'medium',
      contactPreference: 'email',
    },
    mode: 'onChange',
  });

  // Feedback form
  const feedbackForm = useForm<FeedbackData>({
    resolver: zodResolver(feedbackSchema),
    defaultValues: {
      type: 'suggestion',
      rating: 5,
      anonymous: false,
      followUp: true,
    },
    mode: 'onChange',
  });

  const helpCategories = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      description: 'Basic setup and first steps',
      icon: <Book className="w-5 h-5" />,
      articles: 12
    },
    {
      id: 'papt-framework',
      title: 'PAPT Framework',
      description: 'Understanding Pillars, Areas, Projects, and Tasks',
      icon: <Target className="w-5 h-5" />,
      articles: 8
    },
    {
      id: 'ai-features',
      title: 'AI Features',
      description: 'Making the most of AI assistance',
      icon: <Brain className="w-5 h-5" />,
      articles: 15
    },
    {
      id: 'sync-backup',
      title: 'Sync & Backup',
      description: 'Data synchronization and backup',
      icon: <Cloud className="w-5 h-5" />,
      articles: 6
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      description: 'Common issues and solutions',
      icon: <AlertCircle className="w-5 h-5" />,
      articles: 20
    },
    {
      id: 'advanced',
      title: 'Advanced Features',
      description: 'Power user tips and tricks',
      icon: <Zap className="w-5 h-5" />,
      articles: 10
    }
  ];

  const popularArticles = [
    { id: 1, title: 'How to create your first Pillar', category: 'getting-started', views: 1250 },
    { id: 2, title: 'Understanding the PAPT hierarchy', category: 'papt-framework', views: 980 },
    { id: 3, title: 'Setting up AI suggestions', category: 'ai-features', views: 850 },
    { id: 4, title: 'Syncing across multiple devices', category: 'sync-backup', views: 720 },
    { id: 5, title: 'Fixing sync issues', category: 'troubleshooting', views: 650 }
  ];

  const quickLinks = [
    { title: 'Video Tutorials', icon: <Video className="w-4 h-4" />, url: '#', external: true },
    { title: 'Community Forum', icon: <MessageCircle className="w-4 h-4" />, url: '#', external: true },
    { title: 'Feature Requests', icon: <ThumbsUp className="w-4 h-4" />, url: '#', external: true },
    { title: 'Release Notes', icon: <FileText className="w-4 h-4" />, url: '#', external: true },
  ];

  // Handle support request submission
  const handleSupportSubmit = async (data: SupportRequestData) => {
    setIsSubmittingSupport(true);
    
    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      supportForm.reset();
      toast.success('Support request submitted successfully');
      addNotification({
        type: 'success',
        title: 'Support Request Submitted',
        message: 'We\'ve received your support request and will respond within 24 hours.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to submit support request');
    } finally {
      setIsSubmittingSupport(false);
    }
  };

  // Handle feedback submission
  const handleFeedbackSubmit = async (data: FeedbackData) => {
    setIsSubmittingFeedback(true);
    
    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      feedbackForm.reset();
      toast.success('Feedback submitted successfully');
      addNotification({
        type: 'success',
        title: 'Feedback Received',
        message: 'Thank you for your feedback! It helps us improve Aurum Life.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to submit feedback');
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const filteredCategories = helpCategories.filter(category =>
    searchQuery === '' || 
    category.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredArticles = popularArticles.filter(article =>
    searchQuery === '' || 
    article.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-[rgba(244,208,63,0.05)] p-1 rounded-lg border border-[rgba(244,208,63,0.1)]">
        <Button
          variant={activeTab === 'help' ? 'default' : 'ghost'}
          className={`flex-1 ${activeTab === 'help' ? 'bg-[#F4D03F] text-[#0B0D14]' : 'text-[#B8BCC8] hover:text-[#F4D03F]'}`}
          onClick={() => setActiveTab('help')}
        >
          <HelpCircle className="w-4 h-4 mr-2" />
          Help Center
        </Button>
        <Button
          variant={activeTab === 'support' ? 'default' : 'ghost'}
          className={`flex-1 ${activeTab === 'support' ? 'bg-[#F4D03F] text-[#0B0D14]' : 'text-[#B8BCC8] hover:text-[#F4D03F]'}`}
          onClick={() => setActiveTab('support')}
        >
          <MessageCircle className="w-4 h-4 mr-2" />
          Contact Support
        </Button>
        <Button
          variant={activeTab === 'feedback' ? 'default' : 'ghost'}
          className={`flex-1 ${activeTab === 'feedback' ? 'bg-[#F4D03F] text-[#0B0D14]' : 'text-[#B8BCC8] hover:text-[#F4D03F]'}`}
          onClick={() => setActiveTab('feedback')}
        >
          <Star className="w-4 h-4 mr-2" />
          Send Feedback
        </Button>
      </div>

      {/* Help Center Tab */}
      {activeTab === 'help' && (
        <div className="space-y-6">
          {/* Search */}
          <Card className="glassmorphism-card border-0">
            <CardContent className="p-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#B8BCC8]" />
                <Input
                  placeholder="Search help articles..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
              </div>
            </CardContent>
          </Card>

          {/* Quick Links */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white">Quick Links</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Popular resources and community links
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {quickLinks.map((link, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start"
                  >
                    {link.icon}
                    <span className="ml-3">{link.title}</span>
                    {link.external && <ExternalLink className="w-3 h-3 ml-auto" />}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Help Categories */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white">Help Categories</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Browse help articles by category
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredCategories.map((category) => (
                  <div
                    key={category.id}
                    className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.1)] transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div className="text-[#F4D03F]">{category.icon}</div>
                        <h3 className="text-white font-medium">{category.title}</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                          {category.articles} articles
                        </Badge>
                        <ChevronRight className="w-4 h-4 text-[#B8BCC8]" />
                      </div>
                    </div>
                    <p className="text-[#B8BCC8] text-sm">{category.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Popular Articles */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white">Popular Articles</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Most viewed help articles this week
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {filteredArticles.map((article) => (
                  <div
                    key={article.id}
                    className="flex items-center justify-between p-3 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.1)] transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="w-4 h-4 text-[#F4D03F]" />
                      <div>
                        <h4 className="text-white font-medium">{article.title}</h4>
                        <p className="text-[#B8BCC8] text-sm capitalize">{article.category.replace('-', ' ')}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[#B8BCC8] text-sm">{article.views} views</span>
                      <ChevronRight className="w-4 h-4 text-[#B8BCC8]" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Contact Support Tab */}
      {activeTab === 'support' && (
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <MessageCircle className="w-5 h-5 text-[#F4D03F]" />
              <span>Contact Support</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Get help from our support team. We typically respond within 24 hours.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={supportForm.handleSubmit(handleSupportSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category" className="text-white">Category</Label>
                  <Controller
                    name="category"
                    control={supportForm.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="bug">Bug Report</SelectItem>
                          <SelectItem value="feature">Feature Request</SelectItem>
                          <SelectItem value="account">Account Issues</SelectItem>
                          <SelectItem value="billing">Billing Questions</SelectItem>
                          <SelectItem value="general">General Support</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {supportForm.formState.errors.category && (
                    <p className="text-[#EF4444] text-sm mt-1">{supportForm.formState.errors.category.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="priority" className="text-white">Priority</Label>
                  <Controller
                    name="priority"
                    control={supportForm.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low - General inquiry</SelectItem>
                          <SelectItem value="medium">Medium - Standard issue</SelectItem>
                          <SelectItem value="high">High - Urgent issue</SelectItem>
                          <SelectItem value="urgent">Urgent - Critical problem</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {supportForm.formState.errors.priority && (
                    <p className="text-[#EF4444] text-sm mt-1">{supportForm.formState.errors.priority.message}</p>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="subject" className="text-white">Subject</Label>
                <Input
                  id="subject"
                  {...supportForm.register('subject')}
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  placeholder="Brief description of your issue"
                />
                {supportForm.formState.errors.subject && (
                  <p className="text-[#EF4444] text-sm mt-1">{supportForm.formState.errors.subject.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="description" className="text-white">Description</Label>
                <Textarea
                  id="description"
                  {...supportForm.register('description')}
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white min-h-32"
                  placeholder="Please provide as much detail as possible about your issue, including steps to reproduce if applicable..."
                  rows={6}
                />
                <div className="flex justify-between items-center mt-1">
                  {supportForm.formState.errors.description && (
                    <p className="text-[#EF4444] text-sm">{supportForm.formState.errors.description.message}</p>
                  )}
                  <p className="text-[#B8BCC8] text-sm ml-auto">
                    {supportForm.watch('description')?.length || 0}/2000
                  </p>
                </div>
              </div>

              <div>
                <Label htmlFor="contactPreference" className="text-white">Preferred Contact Method</Label>
                <Controller
                  name="contactPreference"
                  control={supportForm.control}
                  render={({ field }) => (
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                        <SelectValue placeholder="Select contact method" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="email">Email</SelectItem>
                        <SelectItem value="phone">Phone</SelectItem>
                        <SelectItem value="chat">Live Chat</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                />
                {supportForm.formState.errors.contactPreference && (
                  <p className="text-[#EF4444] text-sm mt-1">{supportForm.formState.errors.contactPreference.message}</p>
                )}
              </div>

              <div className="flex space-x-4">
                <Button 
                  type="submit"
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  disabled={isSubmittingSupport}
                >
                  {isSubmittingSupport ? (
                    <CheckCircle2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4 mr-2" />
                  )}
                  {isSubmittingSupport ? 'Submitting...' : 'Submit Request'}
                </Button>
                <Button 
                  type="button"
                  variant="outline" 
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                  onClick={() => supportForm.reset()}
                  disabled={isSubmittingSupport}
                >
                  Clear Form
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Send Feedback Tab */}
      {activeTab === 'feedback' && (
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Star className="w-5 h-5 text-[#F4D03F]" />
              <span>Send Feedback</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Help us improve Aurum Life by sharing your thoughts and suggestions.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={feedbackForm.handleSubmit(handleFeedbackSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="feedbackType" className="text-white">Feedback Type</Label>
                  <Controller
                    name="type"
                    control={feedbackForm.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="praise">Praise - Something you love</SelectItem>
                          <SelectItem value="suggestion">Suggestion - Ideas for improvement</SelectItem>
                          <SelectItem value="complaint">Complaint - Something that needs fixing</SelectItem>
                          <SelectItem value="question">Question - Need clarification</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {feedbackForm.formState.errors.type && (
                    <p className="text-[#EF4444] text-sm mt-1">{feedbackForm.formState.errors.type.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="rating" className="text-white">Overall Rating</Label>
                  <Controller
                    name="rating"
                    control={feedbackForm.control}
                    render={({ field }) => (
                      <div className="mt-2 flex items-center space-x-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Button
                            key={star}
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="p-1"
                            onClick={() => field.onChange(star)}
                          >
                            <Star 
                              className={`w-6 h-6 ${
                                star <= field.value 
                                  ? 'text-[#F4D03F] fill-[#F4D03F]' 
                                  : 'text-[#B8BCC8]'
                              }`}
                            />
                          </Button>
                        ))}
                        <span className="text-[#B8BCC8] text-sm ml-2">
                          ({field.value}/5 stars)
                        </span>
                      </div>
                    )}
                  />
                  {feedbackForm.formState.errors.rating && (
                    <p className="text-[#EF4444] text-sm mt-1">{feedbackForm.formState.errors.rating.message}</p>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="feedback" className="text-white">Your Feedback</Label>
                <Textarea
                  id="feedback"
                  {...feedbackForm.register('feedback')}
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white min-h-32"
                  placeholder="Share your thoughts, suggestions, or concerns..."
                  rows={6}
                />
                <div className="flex justify-between items-center mt-1">
                  {feedbackForm.formState.errors.feedback && (
                    <p className="text-[#EF4444] text-sm">{feedbackForm.formState.errors.feedback.message}</p>
                  )}
                  <p className="text-[#B8BCC8] text-sm ml-auto">
                    {feedbackForm.watch('feedback')?.length || 0}/1000
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Submit Anonymously</Label>
                    <p className="text-[#B8BCC8] text-sm">Hide your identity when submitting feedback</p>
                  </div>
                  <Controller
                    name="anonymous"
                    control={feedbackForm.control}
                    render={({ field }) => (
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    )}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Allow Follow-up</Label>
                    <p className="text-[#B8BCC8] text-sm">We may contact you for additional information</p>
                  </div>
                  <Controller
                    name="followUp"
                    control={feedbackForm.control}
                    render={({ field }) => (
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    )}
                  />
                </div>
              </div>

              <div className="flex space-x-4">
                <Button 
                  type="submit"
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  disabled={isSubmittingFeedback}
                >
                  {isSubmittingFeedback ? (
                    <CheckCircle2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4 mr-2" />
                  )}
                  {isSubmittingFeedback ? 'Submitting...' : 'Send Feedback'}
                </Button>
                <Button 
                  type="button"
                  variant="outline" 
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                  onClick={() => feedbackForm.reset()}
                  disabled={isSubmittingFeedback}
                >
                  Clear Form
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}