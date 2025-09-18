import { useEffect, useState } from 'react';
import { motion, PanInfo, useDragControls } from 'motion/react';
import { Home, Calendar, CheckSquare, Target, Settings, Plus } from 'lucide-react';
import { useAppStore } from '../../stores/basicAppStore';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

interface SwipeGestureProps {
  children: React.ReactNode;
  onSwipeRight?: () => void;
  onSwipeLeft?: () => void;
  className?: string;
}

export function SwipeGesture({ children, onSwipeRight, onSwipeLeft, className }: SwipeGestureProps) {
  const [isDragging, setIsDragging] = useState(false);
  
  const handleDrag = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const threshold = 100;
    const velocity = 500;
    
    if (Math.abs(info.offset.x) > threshold || Math.abs(info.velocity.x) > velocity) {
      if (info.offset.x > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (info.offset.x < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }
  };

  return (
    <motion.div
      className={cn("touch-target", className)}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDrag={handleDrag}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => setIsDragging(false)}
      whileDrag={{ scale: 0.98 }}
      style={{ touchAction: 'pan-x' }}
    >
      {children}
    </motion.div>
  );
}

interface BottomNavigationProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  className?: string;
}

export function BottomNavigation({ activeSection, onSectionChange, className }: BottomNavigationProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Home' },
    { id: 'today', icon: Calendar, label: 'Today' },
    { id: 'tasks', icon: CheckSquare, label: 'Tasks' },
    { id: 'areas', icon: Target, label: 'Areas' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <motion.nav
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50 lg:hidden",
        "glassmorphism-card border-t border-border/50 rounded-t-xl",
        "px-2 py-2 mx-2 mb-2",
        "safe-area-inset-bottom", // Handle iPhone notch/home indicator
        className
      )}
      style={{ paddingBottom: 'calc(0.5rem + env(safe-area-inset-bottom))' }}
      initial={{ y: 100 }}
      animate={{ y: isVisible ? 0 : 100 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="flex items-center justify-around max-w-md mx-auto">
        {navItems.map(({ id, icon: Icon, label }) => (
          <Button
            key={id}
            variant="ghost"
            size="sm"
            onClick={() => onSectionChange(id)}
            className={cn(
              "flex flex-col items-center gap-1 h-14 px-2 py-2",
              "text-xs touch-target min-h-[48px] min-w-[48px]",
              activeSection === id 
                ? "text-primary bg-primary/10" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[10px] font-medium leading-tight">{label}</span>
          </Button>
        ))}
      </div>
    </motion.nav>
  );
}

interface TouchOptimizedButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}

export function TouchOptimizedButton({ 
  children, 
  onClick, 
  variant = 'default', 
  size = 'md', 
  disabled = false,
  className 
}: TouchOptimizedButtonProps) {
  const sizeClasses = {
    sm: 'min-h-[44px] min-w-[44px] px-4 py-2',
    md: 'min-h-[48px] min-w-[48px] px-6 py-3',
    lg: 'min-h-[52px] min-w-[52px] px-8 py-4'
  };

  const variantClasses = {
    default: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-accent text-accent-foreground hover:bg-accent/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground'
  };

  return (
    <motion.button
      className={cn(
        "touch-target flex items-center justify-center",
        "rounded-lg font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "disabled:pointer-events-none disabled:opacity-50",
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      onClick={onClick}
      disabled={disabled}
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
    >
      {children}
    </motion.button>
  );
}

interface OneHandedLayoutProps {
  children: React.ReactNode;
  actionButton?: React.ReactNode;
  className?: string;
}

export function OneHandedLayout({ children, actionButton, className }: OneHandedLayoutProps) {
  return (
    <div className={cn("relative min-h-screen pb-32 lg:pb-0", className)}>
      <div className="container-responsive">
        {children}
      </div>
      
      {/* Floating action in thumb-friendly zone - positioned above bottom nav */}
      {actionButton && (
        <div className="fixed right-4 z-40 lg:hidden mobile-fab-position" style={{ bottom: 'calc(6.5rem + env(safe-area-inset-bottom))' }}>
          {actionButton}
        </div>
      )}
    </div>
  );
}

interface MobilePullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  className?: string;
}

export function MobilePullToRefresh({ onRefresh, children, className }: MobilePullToRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const dragControls = useDragControls();

  const handleDrag = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (info.offset.y > 0 && window.scrollY === 0) {
      setPullDistance(Math.min(info.offset.y, 100));
    }
  };

  const handleDragEnd = async (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (info.offset.y > 80 && window.scrollY === 0) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
      }
    }
    setPullDistance(0);
  };

  return (
    <motion.div
      className={cn("touch-action-pan-y", className)}
      drag="y"
      dragControls={dragControls}
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.2}
      onDrag={handleDrag}
      onDragEnd={handleDragEnd}
      style={{ y: pullDistance }}
    >
      {pullDistance > 0 && (
        <motion.div
          className="absolute top-0 left-0 right-0 flex items-center justify-center py-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: pullDistance / 80 }}
        >
          <div className="text-sm text-muted-foreground">
            {pullDistance > 80 ? 'Release to refresh' : 'Pull to refresh'}
          </div>
        </motion.div>
      )}
      
      {isRefreshing && (
        <motion.div
          className="absolute top-0 left-0 right-0 flex items-center justify-center py-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            Refreshing...
          </div>
        </motion.div>
      )}
      
      {children}
    </motion.div>
  );
}

export function useMobileDetection() {
  const [isMobile, setIsMobile] = useState(false);
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      setIsTouch('ontouchstart' in window || navigator.maxTouchPoints > 0);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return { isMobile, isTouch };
}