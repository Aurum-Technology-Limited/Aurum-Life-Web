import { useState } from 'react';
import { Settings as SettingsIcon, User, Bell, Palette, Brain, Cloud, Shield, HelpCircle, ChevronRight } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';

// Simple lightweight settings sections
const SimpleAccountSettings = () => (
  <Card className="glassmorphism-card border-0">
    <CardHeader>
      <CardTitle className="text-white">Account & Profile</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <label className="text-[#B8BCC8] text-sm">Name</label>
        <div className="text-white">John Doe</div>
      </div>
      <div>
        <label className="text-[#B8BCC8] text-sm">Email</label>
        <div className="text-white">john.doe@example.com</div>
      </div>
      <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
        Edit Profile
      </Button>
    </CardContent>
  </Card>
);

const SimplePreferencesSettings = () => (
  <Card className="glassmorphism-card border-0">
    <CardHeader>
      <CardTitle className="text-white">App Preferences</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="text-[#B8BCC8]">
        Theme: Aurum Dark Gold (Default)
      </div>
      <div className="text-[#B8BCC8]">
        Language: English
      </div>
      <div className="text-[#B8BCC8]">
        Timezone: Auto-detect
      </div>
    </CardContent>
  </Card>
);

const SimpleNotificationSettings = () => (
  <Card className="glassmorphism-card border-0">
    <CardHeader>
      <CardTitle className="text-white">Notifications</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="text-[#B8BCC8]">
        Email notifications: Enabled
      </div>
      <div className="text-[#B8BCC8]">
        Push notifications: Enabled
      </div>
      <div className="text-[#B8BCC8]">
        Daily summaries: Enabled
      </div>
    </CardContent>
  </Card>
);

const SimpleHelpSettings = () => (
  <Card className="glassmorphism-card border-0">
    <CardHeader>
      <CardTitle className="text-white">Help & Support</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
        View Documentation
      </Button>
      <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
        Contact Support
      </Button>
      <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
        Send Feedback
      </Button>
    </CardContent>
  </Card>
);

export default function SimpleSettings() {
  const [activeSection, setActiveSection] = useState('account');

  const sections = [
    { id: 'account', label: 'Account', icon: User, component: SimpleAccountSettings },
    { id: 'preferences', label: 'Preferences', icon: Palette, component: SimplePreferencesSettings },
    { id: 'notifications', label: 'Notifications', icon: Bell, component: SimpleNotificationSettings },
    { id: 'help', label: 'Help', icon: HelpCircle, component: SimpleHelpSettings },
  ];

  const ActiveComponent = sections.find(s => s.id === activeSection)?.component || SimpleAccountSettings;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
          <SettingsIcon className="w-6 h-6 text-[#0B0D14]" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-[#B8BCC8]">Customize your Aurum Life experience</p>
        </div>
      </div>

      {/* User Profile */}
      <Card className="glassmorphism-card border-0">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <Avatar className="w-16 h-16">
              <AvatarFallback className="bg-[#F4D03F] text-[#0B0D14] text-xl font-bold">JD</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h3 className="text-xl font-medium text-white">John Doe</h3>
              <p className="text-[#B8BCC8]">john.doe@example.com</p>
              <Badge className="mt-2 bg-[#F4D03F] text-[#0B0D14]">Premium Member</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation */}
        <div className="lg:col-span-1">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white">Settings Menu</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <nav className="space-y-1">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <Button
                      key={section.id}
                      variant="ghost"
                      className={`w-full justify-start ${
                        activeSection === section.id
                          ? 'bg-[rgba(244,208,63,0.1)] text-[#F4D03F]'
                          : 'text-[#B8BCC8] hover:text-[#F4D03F]'
                      }`}
                      onClick={() => setActiveSection(section.id)}
                    >
                      <Icon className="w-4 h-4 mr-3" />
                      {section.label}
                      <ChevronRight className="w-4 h-4 ml-auto" />
                    </Button>
                  );
                })}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <ActiveComponent />
        </div>
      </div>
    </div>
  );
}