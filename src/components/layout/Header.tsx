import { useState } from 'react';
import { Search, Bell, User, Menu, LogOut } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { useAuthStore } from '../../stores/authStore';
import { useNotifications } from '../../hooks/useNotifications';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

interface HeaderProps {
  onSectionChange?: (section: string) => void;
  onNotificationsOpen?: () => void;
  onMobileMenuOpen?: () => void;
}

export default function Header({ onSectionChange, onNotificationsOpen, onMobileMenuOpen }: HeaderProps) {
  const { signOut, user } = useAuthStore();
  const { unreadCount } = useNotifications();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      console.log('Searching for:', searchQuery);
      // TODO: Implement global search functionality
      // Could search across pillars, areas, projects, tasks, etc.
    }
  };
  return (
    <header className="glassmorphism-header sticky top-0 z-50 px-6 py-4 h-20">
      <div className="flex items-center justify-between">
        {/* Mobile Menu Button & Logo Section */}
        <div className="flex items-center space-x-3 w-64 lg:w-64">
          {/* Mobile Menu Button */}
          <Button 
            variant="ghost" 
            size="icon"
            onClick={onMobileMenuOpen}
            className="lg:hidden text-muted-foreground hover:text-primary hover:bg-primary/10 shrink-0"
          >
            <Menu className="w-5 h-5" />
          </Button>
          
          <div className="w-8 h-8 flex items-center justify-center shrink-0">
            <img 
              src={aurumLogo} 
              alt="Aurum Life Logo" 
              className="w-8 h-8 object-contain"
            />
          </div>
          <span className="text-lg font-semibold aurum-text-gradient truncate">
            Aurum Life
          </span>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-lg mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              className="pl-10 bg-input border-border text-foreground placeholder:text-muted-foreground focus:border-primary"
              placeholder="Search pillars, areas, projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleSearch}
            />
          </div>
        </div>

        {/* User Actions */}
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={onNotificationsOpen}
            className="text-muted-foreground hover:text-primary hover:bg-primary/10 relative"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <Badge 
                variant="default" 
                className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              >
                {unreadCount > 99 ? '99+' : unreadCount}
              </Badge>
            )}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon"
                className="text-muted-foreground hover:text-primary hover:bg-primary/10"
              >
                <User className="w-5 h-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              className="glassmorphism-card border-0 bg-card text-card-foreground min-w-[200px]"
            >
              <DropdownMenuItem 
                onClick={() => onSectionChange?.('settings')}
                className="hover:bg-[rgba(244,208,63,0.1)] focus:bg-[rgba(244,208,63,0.1)] cursor-pointer"
              >
                <User className="w-4 h-4 mr-2" />
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={onNotificationsOpen}
                className="hover:bg-[rgba(244,208,63,0.1)] focus:bg-[rgba(244,208,63,0.1)] cursor-pointer"
              >
                <Bell className="w-4 h-4 mr-2" />
                Notifications
              </DropdownMenuItem>
              
              <DropdownMenuSeparator className="bg-[rgba(244,208,63,0.2)]" />
              
              <DropdownMenuItem 
                onClick={signOut}
                className="hover:bg-[rgba(239,68,68,0.1)] focus:bg-[rgba(239,68,68,0.1)] cursor-pointer text-[#EF4444] hover:text-[#EF4444] focus:text-[#EF4444]"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </DropdownMenuItem>

            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}