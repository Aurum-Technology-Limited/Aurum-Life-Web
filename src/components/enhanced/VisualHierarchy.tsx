import { motion } from 'motion/react';
import { ChevronRight, Star, ArrowRight, Zap } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';

interface ActionableCardProps {
  title: string;
  description?: string;
  priority: 'primary' | 'secondary' | 'tertiary';
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ComponentType<{ className?: string }>;
  };
  badge?: {
    text: string;
    variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  };
  children?: React.ReactNode;
  className?: string;
}

export function ActionableCard({
  title,
  description,
  priority,
  action,
  badge,
  children,
  className
}: ActionableCardProps) {
  const priorityStyles = {
    primary: {
      card: "border-primary/50 bg-primary/5 shadow-lg shadow-primary/10",
      title: "text-primary text-lg font-semibold",
      action: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md"
    },
    secondary: {
      card: "border-border/50 bg-muted/30",
      title: "text-foreground font-medium",
      action: "bg-secondary text-secondary-foreground hover:bg-secondary/80"
    },
    tertiary: {
      card: "border-border/30 bg-muted/10",
      title: "text-muted-foreground",
      action: "bg-muted text-muted-foreground hover:bg-muted/80"
    }
  };

  const styles = priorityStyles[priority];
  const ActionIcon = action?.icon || ArrowRight;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      <Card className={cn("glassmorphism-card transition-all duration-200", styles.card)}>
        <CardHeader className={priority === 'primary' ? "pb-4" : "pb-3"}>
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <CardTitle className={cn("line-clamp-2", styles.title)}>
                  {title}
                </CardTitle>
                {badge && (
                  <Badge 
                    variant={badge.variant || 'default'}
                    className="shrink-0"
                  >
                    {badge.text}
                  </Badge>
                )}
              </div>
              {description && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {description}
                </p>
              )}
            </div>
            
            {priority === 'primary' && (
              <Star className="w-5 h-5 text-primary shrink-0 ml-2" />
            )}
          </div>
        </CardHeader>

        {children && (
          <CardContent className="pt-0">
            {children}
          </CardContent>
        )}

        {action && (
          <CardContent className="pt-0">
            <Button
              onClick={action.onClick}
              className={cn(
                "w-full justify-between group",
                styles.action
              )}
              size={priority === 'primary' ? 'default' : 'sm'}
            >
              <span>{action.label}</span>
              <ActionIcon className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
}

interface ContentHierarchyProps {
  level: 1 | 2 | 3 | 4;
  title: string;
  subtitle?: string;
  actions?: Array<{
    label: string;
    onClick: () => void;
    variant?: 'default' | 'outline' | 'ghost';
    primary?: boolean;
  }>;
  children?: React.ReactNode;
  className?: string;
}

export function ContentHierarchy({
  level,
  title,
  subtitle,
  actions = [],
  children,
  className
}: ContentHierarchyProps) {
  const levelStyles = {
    1: {
      container: "space-y-8",
      header: "space-y-4 mb-8 pb-6 border-b border-border/50",
      title: "text-3xl font-bold text-foreground",
      subtitle: "text-lg text-muted-foreground",
      actions: "flex flex-wrap gap-3"
    },
    2: {
      container: "space-y-6",
      header: "space-y-3 mb-6 pb-4 border-b border-border/30",
      title: "text-2xl font-semibold text-foreground",
      subtitle: "text-base text-muted-foreground",
      actions: "flex flex-wrap gap-2"
    },
    3: {
      container: "space-y-4",
      header: "space-y-2 mb-4",
      title: "text-xl font-medium text-foreground",
      subtitle: "text-sm text-muted-foreground",
      actions: "flex flex-wrap gap-2"
    },
    4: {
      container: "space-y-3",
      header: "space-y-1 mb-3",
      title: "text-lg font-medium text-foreground",
      subtitle: "text-sm text-muted-foreground",
      actions: "flex flex-wrap gap-1"
    }
  };

  const styles = levelStyles[level];

  const primaryAction = actions.find(action => action.primary);
  const secondaryActions = actions.filter(action => !action.primary);

  return (
    <div className={cn(styles.container, className)}>
      <div className={styles.header}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h1 className={styles.title}>{title}</h1>
            {subtitle && (
              <p className={styles.subtitle}>{subtitle}</p>
            )}
          </div>
          
          {actions.length > 0 && (
            <div className={styles.actions}>
              {primaryAction && (
                <Button
                  onClick={primaryAction.onClick}
                  variant={primaryAction.variant || 'default'}
                  className="shadow-md"
                >
                  {primaryAction.label}
                </Button>
              )}
              {secondaryActions.map((action, index) => (
                <Button
                  key={index}
                  onClick={action.onClick}
                  variant={action.variant || 'outline'}
                  size={level > 2 ? 'sm' : 'default'}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {children}
    </div>
  );
}

interface ProgressiveDisclosureProps {
  title: string;
  summary: string;
  expanded?: boolean;
  onToggle?: (expanded: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

export function ProgressiveDisclosure({
  title,
  summary,
  expanded = false,
  onToggle,
  children,
  className
}: ProgressiveDisclosureProps) {
  return (
    <Card className={cn("glassmorphism-card overflow-hidden", className)}>
      <motion.button
        className="w-full text-left p-4 hover:bg-muted/20 transition-colors"
        onClick={() => onToggle?.(!expanded)}
        whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
      >
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-foreground mb-1">{title}</h3>
            <p className="text-sm text-muted-foreground line-clamp-2">{summary}</p>
          </div>
          
          <motion.div
            animate={{ rotate: expanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight className="w-5 h-5 text-muted-foreground" />
          </motion.div>
        </div>
      </motion.button>
      
      <motion.div
        initial={false}
        animate={{
          height: expanded ? 'auto' : 0,
          opacity: expanded ? 1 : 0
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="overflow-hidden"
      >
        <div className="px-4 pb-4 border-t border-border/30">
          {children}
        </div>
      </motion.div>
    </Card>
  );
}

interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'info' | 'pending' | 'inactive';
  label: string;
  description?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StatusIndicator({
  status,
  label,
  description,
  showIcon = true,
  size = 'md',
  className
}: StatusIndicatorProps) {
  const statusConfig = {
    success: {
      color: 'text-green-400',
      bg: 'bg-green-400/10',
      border: 'border-green-400/20',
      dot: 'bg-green-400'
    },
    warning: {
      color: 'text-yellow-400',
      bg: 'bg-yellow-400/10',
      border: 'border-yellow-400/20',
      dot: 'bg-yellow-400'
    },
    error: {
      color: 'text-red-400',
      bg: 'bg-red-400/10',
      border: 'border-red-400/20',
      dot: 'bg-red-400'
    },
    info: {
      color: 'text-blue-400',
      bg: 'bg-blue-400/10',
      border: 'border-blue-400/20',
      dot: 'bg-blue-400'
    },
    pending: {
      color: 'text-purple-400',
      bg: 'bg-purple-400/10',
      border: 'border-purple-400/20',
      dot: 'bg-purple-400'
    },
    inactive: {
      color: 'text-muted-foreground',
      bg: 'bg-muted/10',
      border: 'border-muted/20',
      dot: 'bg-muted-foreground'
    }
  };

  const config = statusConfig[status];
  
  const sizeClasses = {
    sm: {
      container: 'px-2 py-1 text-xs',
      dot: 'w-1.5 h-1.5',
      icon: 'w-3 h-3'
    },
    md: {
      container: 'px-3 py-1.5 text-sm',
      dot: 'w-2 h-2',
      icon: 'w-4 h-4'
    },
    lg: {
      container: 'px-4 py-2 text-base',
      dot: 'w-2.5 h-2.5',
      icon: 'w-5 h-5'
    }
  };

  const sizeClass = sizeClasses[size];

  return (
    <div className={cn(
      "inline-flex items-center gap-2 rounded-full border",
      config.bg,
      config.border,
      sizeClass.container,
      className
    )}>
      {showIcon && (
        <div className={cn(
          "rounded-full shrink-0",
          config.dot,
          sizeClass.dot
        )} />
      )}
      
      <div className="flex-1 min-w-0">
        <span className={cn("font-medium", config.color)}>
          {label}
        </span>
        {description && (
          <span className="text-muted-foreground ml-1">
            {description}
          </span>
        )}
      </div>
    </div>
  );
}

interface CallToActionProps {
  title: string;
  description: string;
  action: {
    label: string;
    onClick: () => void;
    icon?: React.ComponentType<{ className?: string }>;
  };
  variant?: 'primary' | 'secondary' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function CallToAction({
  title,
  description,
  action,
  variant = 'primary',
  size = 'md',
  className
}: CallToActionProps) {
  const variantStyles = {
    primary: "bg-gradient-to-r from-primary/20 to-primary/10 border-primary/30",
    secondary: "bg-gradient-to-r from-secondary/20 to-secondary/10 border-secondary/30",
    accent: "bg-gradient-to-r from-accent/20 to-accent/10 border-accent/30"
  };

  const ActionIcon = action.icon || Zap;

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={className}
    >
      <Card className={cn(
        "glassmorphism-card border-2 cursor-pointer transition-all duration-200",
        variantStyles[variant],
        size === 'lg' ? 'p-8' : size === 'md' ? 'p-6' : 'p-4'
      )}>
        <CardContent className="text-center space-y-4 p-0">
          <div className="space-y-2">
            <h3 className={cn(
              "font-semibold text-foreground",
              size === 'lg' ? 'text-2xl' : size === 'md' ? 'text-xl' : 'text-lg'
            )}>
              {title}
            </h3>
            <p className={cn(
              "text-muted-foreground",
              size === 'lg' ? 'text-base' : 'text-sm'
            )}>
              {description}
            </p>
          </div>
          
          <Button
            onClick={action.onClick}
            size={size}
            className="shadow-lg group"
          >
            <ActionIcon className="w-4 h-4 mr-2 transition-transform group-hover:scale-110" />
            {action.label}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}