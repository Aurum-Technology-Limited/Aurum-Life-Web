import { useState, useEffect } from 'react';
import { Shield, Settings, X, Check, AlertTriangle, Info } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { ScrollArea } from '../ui/scroll-area';
import { motion, AnimatePresence } from 'motion/react';
import { usePrivacyConsent } from '../../hooks/usePrivacyConsent';
import { toast } from 'sonner@2.0.3';

export default function ConsentBanner() {
  const {
    getConsentBanner,
    grantConsent,
    revokeConsent,
    hasConsent,
    status,
    isLoading
  } = usePrivacyConsent();

  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [bannerData, setBannerData] = useState({ show: false, message: '', actions: [] });
  const [customConsents, setCustomConsents] = useState({
    data_collection: false,
    ai_analysis: false,
    performance_analytics: false,
    marketing: false,
    third_party_integrations: false,
  });

  useEffect(() => {
    try {
      const data = getConsentBanner();
      setBannerData(data);
      setShowBanner(false); // Disable banner by default to prevent API errors
      
      // Initialize custom consent state with safe defaults
      setCustomConsents({
        data_collection: true, // Essential - default true
        ai_analysis: true,
        performance_analytics: false,
        marketing: false,
        third_party_integrations: false,
      });
    } catch (error) {
      console.log('Consent banner initialization failed:', error);
      setShowBanner(false);
    }
  }, [getConsentBanner]);

  const handleAcceptAll = async () => {
    try {
      await grantConsent('data_collection');
      await grantConsent('ai_analysis');
      await grantConsent('performance_analytics');
      await grantConsent('marketing');
      await grantConsent('third_party_integrations');
      
      setShowBanner(false);
      toast.success('All consents granted successfully');
    } catch (error) {
      toast.error('Failed to grant consents');
    }
  };

  const handleRejectNonEssential = async () => {
    try {
      await grantConsent('data_collection'); // Essential only
      await revokeConsent('ai_analysis');
      await revokeConsent('performance_analytics');
      await revokeConsent('marketing');
      await revokeConsent('third_party_integrations');
      
      setShowBanner(false);
      toast.success('Essential consents granted');
    } catch (error) {
      toast.error('Failed to update consents');
    }
  };

  const handleCustomConsent = async (type: keyof typeof customConsents, granted: boolean) => {
    try {
      if (granted) {
        await grantConsent(type);
      } else {
        await revokeConsent(type);
      }
      
      setCustomConsents(prev => ({ ...prev, [type]: granted }));
      toast.success(`${type.replace('_', ' ')} consent ${granted ? 'granted' : 'revoked'}`);
    } catch (error) {
      toast.error(`Failed to update ${type} consent`);
    }
  };

  const handleSaveCustom = () => {
    setShowBanner(false);
    setShowDetails(false);
    toast.success('Consent preferences saved');
  };

  if (!showBanner) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-[rgba(11,13,20,0.95)] backdrop-blur-lg border-t border-[rgba(244,208,63,0.2)]"
      >
        <div className="max-w-6xl mx-auto">
          <Card className="glassmorphism-card border-0 bg-[rgba(26,29,41,0.9)]">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="w-10 h-10 bg-[rgba(244,208,63,0.1)] rounded-lg flex items-center justify-center">
                    <Shield className="w-6 h-6 text-[#F4D03F]" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-white">Privacy & Data Consent</h3>
                      <Badge variant="outline" className="text-[#F4D03F] border-[#F4D03F]">
                        Required
                      </Badge>
                    </div>
                    <p className="text-[#B8BCC8] mb-4 max-w-2xl">
                      {bannerData.message || 'We need your consent to provide you with the best Aurum Life experience while respecting your privacy.'}
                    </p>
                    
                    <div className="flex flex-wrap gap-3">
                      {/* Quick Actions */}
                      <Button
                        onClick={handleAcceptAll}
                        disabled={isLoading}
                        className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                      >
                        <Check className="w-4 h-4 mr-2" />
                        Accept All
                      </Button>
                      
                      <Button
                        onClick={handleRejectNonEssential}
                        disabled={isLoading}
                        variant="outline"
                        className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                      >
                        Essential Only
                      </Button>

                      {/* Customize Button with Dialog */}
                      <Dialog open={showDetails} onOpenChange={setShowDetails}>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                          >
                            <Settings className="w-4 h-4 mr-2" />
                            Customize
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="glassmorphism-card border-0 max-w-2xl max-h-[80vh]">
                          <DialogHeader>
                            <DialogTitle className="text-white flex items-center space-x-2">
                              <Shield className="w-5 h-5 text-[#F4D03F]" />
                              <span>Customize Consent Preferences</span>
                            </DialogTitle>
                            <DialogDescription className="text-[#B8BCC8]">
                              Choose exactly what data we can collect and how we can use it
                            </DialogDescription>
                          </DialogHeader>
                          
                          <ScrollArea className="max-h-96">
                            <div className="space-y-6 p-1">
                              {/* Data Collection */}
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <Label className="text-white font-medium">Essential Data Collection</Label>
                                    <p className="text-[#B8BCC8] text-sm">
                                      Required for core functionality and security
                                    </p>
                                  </div>
                                  <Switch
                                    checked={customConsents.data_collection}
                                    onCheckedChange={(checked) => handleCustomConsent('data_collection', checked)}
                                    disabled={isLoading}
                                  />
                                </div>
                                <div className="text-xs text-[#6B7280] pl-4 border-l-2 border-[rgba(244,208,63,0.2)]">
                                  Includes: Account information, preferences, tasks, and projects
                                </div>
                              </div>

                              <Separator className="bg-[rgba(244,208,63,0.1)]" />

                              {/* AI Analysis */}
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <Label className="text-white font-medium">AI Analysis & Insights</Label>
                                    <p className="text-[#B8BCC8] text-sm">
                                      Enable AI-powered recommendations and productivity insights
                                    </p>
                                  </div>
                                  <Switch
                                    checked={customConsents.ai_analysis}
                                    onCheckedChange={(checked) => handleCustomConsent('ai_analysis', checked)}
                                    disabled={isLoading}
                                  />
                                </div>
                                <div className="text-xs text-[#6B7280] pl-4 border-l-2 border-[rgba(244,208,63,0.2)]">
                                  Includes: Task pattern analysis, goal recommendations, productivity coaching
                                </div>
                              </div>

                              <Separator className="bg-[rgba(244,208,63,0.1)]" />

                              {/* Performance Analytics */}
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <Label className="text-white font-medium">Performance Analytics</Label>
                                    <p className="text-[#B8BCC8] text-sm">
                                      Anonymous usage analytics to improve the app
                                    </p>
                                  </div>
                                  <Switch
                                    checked={customConsents.performance_analytics}
                                    onCheckedChange={(checked) => handleCustomConsent('performance_analytics', checked)}
                                    disabled={isLoading}
                                  />
                                </div>
                                <div className="text-xs text-[#6B7280] pl-4 border-l-2 border-[rgba(244,208,63,0.2)]">
                                  Includes: App performance metrics, feature usage, crash reports
                                </div>
                              </div>

                              <Separator className="bg-[rgba(244,208,63,0.1)]" />

                              {/* Marketing */}
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <Label className="text-white font-medium">Marketing Communications</Label>
                                    <p className="text-[#B8BCC8] text-sm">
                                      Receive product updates and personalized content
                                    </p>
                                  </div>
                                  <Switch
                                    checked={customConsents.marketing}
                                    onCheckedChange={(checked) => handleCustomConsent('marketing', checked)}
                                    disabled={isLoading}
                                  />
                                </div>
                                <div className="text-xs text-[#6B7280] pl-4 border-l-2 border-[rgba(244,208,63,0.2)]">
                                  Includes: Feature announcements, tips & tricks, promotional content
                                </div>
                              </div>

                              <Separator className="bg-[rgba(244,208,63,0.1)]" />

                              {/* Third Party */}
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <Label className="text-white font-medium">Third-Party Integrations</Label>
                                    <p className="text-[#B8BCC8] text-sm">
                                      Enable integrations with external services
                                    </p>
                                  </div>
                                  <Switch
                                    checked={customConsents.third_party_integrations}
                                    onCheckedChange={(checked) => handleCustomConsent('third_party_integrations', checked)}
                                    disabled={isLoading}
                                  />
                                </div>
                                <div className="text-xs text-[#6B7280] pl-4 border-l-2 border-[rgba(244,208,63,0.2)]">
                                  Includes: Calendar sync, cloud storage, productivity tools
                                </div>
                              </div>
                            </div>
                          </ScrollArea>

                          <div className="flex justify-between pt-4">
                            <Button
                              variant="outline"
                              onClick={() => setShowDetails(false)}
                              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                            >
                              Cancel
                            </Button>
                            <Button
                              onClick={handleSaveCustom}
                              disabled={isLoading}
                              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                            >
                              Save Preferences
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>

                    {/* Status Info */}
                    <div className="flex items-center space-x-2 mt-3 text-xs text-[#6B7280]">
                      <Info className="w-3 h-3" />
                      <span>
                        You can change these preferences anytime in Settings → Privacy & Security
                      </span>
                    </div>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowBanner(false)}
                  className="text-[#6B7280] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}