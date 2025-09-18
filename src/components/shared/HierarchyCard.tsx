import { ReactNode } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ChevronRight, Edit, Trash2, MoreVertical } from 'lucide-react';
import { motion } from 'motion/react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu';

interface SubItem {
  id: string;
  name: string;
  progress?: number;
  healthScore?: number;
  onClick: () => void;
}

interface HierarchyCardProps {
  level: 'pillar' | 'area' | 'project' | 'task';
  title: string;
  description?: string;
  healthScore?: number;
  progress?: number;
  icon?: ReactNode;
  iconBgColor?: string;
  color?: string;
  badge?: {
    text: string;
    variant?: 'default' | 'secondary' | 'outline' | 'destructive';
  };
  metrics?: Array<{
    label: string;
    value: string | number;
    icon?: ReactNode;
    color?: string;
  }>;
  subItems?: SubItem[];
  subItemsTitle?: string;
  children?: ReactNode;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onViewChildren?: () => void; // New prop for "View Tasks", "View Projects", etc.
  isClickable?: boolean;
  className?: string;
  compact?: boolean;
  showDirectActions?: boolean; // New prop to show direct action buttons
}

const levelStyles = {
  pillar: {
    borderClass: 'hierarchy-pillar',
    hoverColor: 'rgba(244,208,63,0.15)',
    accentColor: '#F4D03F',
    bgHover: 'rgba(244,208,63,0.08)',
  },
  area: {
    borderClass: 'hierarchy-area',
    hoverColor: 'rgba(59,130,246,0.15)',
    accentColor: '#3B82F6',
    bgHover: 'rgba(59,130,246,0.08)',
  },
  project: {
    borderClass: 'hierarchy-project',
    hoverColor: 'rgba(16,185,129,0.15)',
    accentColor: '#10B981',
    bgHover: 'rgba(16,185,129,0.08)',
  },
  task: {
    borderClass: 'hierarchy-task',
    hoverColor: 'rgba(139,92,246,0.15)',
    accentColor: '#8B5CF6',
    bgHover: 'rgba(139,92,246,0.08)',
  },
};

export default function HierarchyCard({
  level,
  title,
  description,
  healthScore,
  progress,
  icon,
  iconBgColor,
  color,
  badge,
  metrics = [],
  subItems = [],
  subItemsTitle,
  children,
  onClick,
  onEdit,
  onDelete,
  onViewChildren,
  isClickable = true,
  className = '',
  compact = false,
  showDirectActions = false,
}: HierarchyCardProps) {
  const styles = levelStyles[level];
  const displayProgress = progress ?? healthScore ?? 0;
  const showActions = onEdit || onDelete;

  const cardContent = (
    <Card className={`glassmorphism-card border-0 ${styles.borderClass} group relative overflow-hidden transition-all duration-300 hover:border-opacity-50 ${compact ? 'task-card-compact' : ''} ${className}`}>
      {/* Main Card Content - Clickable */}
      <div 
        className={`${compact ? 'task-card-compact' : 'p-4 sm:p-6'} ${compact ? 'space-y-2' : 'space-y-3 sm:space-y-4'} transition-all duration-300 ${isClickable && onClick ? 'cursor-pointer hover:bg-opacity-50' : ''}`}
        onClick={isClickable && onClick ? onClick : undefined}
        style={isClickable && onClick ? { 
          '--hover-bg': styles.bgHover 
        } as React.CSSProperties : undefined}
      >
        {/* Header Section */}
        <div className={`flex items-start justify-between ${compact ? 'mb-2' : 'mb-4'}`}>
          {/* Badge */}
          {badge && (
            <Badge variant={badge.variant || 'outline'} className={compact ? 'text-xs px-2 py-0.5' : 'text-xs'}>
              {badge.text}
            </Badge>
          )}

          {/* Actions positioned safely in top-right */}
          <div className={`flex items-center ${compact ? 'space-x-0.5' : 'space-x-1'} flex-shrink-0 min-w-[44px] sm:min-w-[72px] justify-end`}>
            {showActions && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className={`${compact ? 'h-6 w-6' : 'h-8 w-8'} p-0 opacity-60 group-hover:opacity-100 transition-all duration-200 touch-target hover:bg-white/10`}
                    onClick={(e) => e.stopPropagation()}
                    type="button"
                  >
                    <MoreVertical className={`${compact ? 'h-3 w-3' : 'h-4 w-4'} text-[#B8BCC8] hover:text-white transition-colors`} />
                    <span className="sr-only">Open menu</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="glassmorphism-card border-0 bg-[#1A1D29] min-w-[120px] z-50">
                  {onEdit && (
                    <DropdownMenuItem onClick={(e) => { 
                      e.stopPropagation(); 
                      onEdit(); 
                    }}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                  )}
                  {onDelete && (
                    <>
                      <DropdownMenuSeparator className="bg-[rgba(244,208,63,0.1)]" />
                      <DropdownMenuItem 
                        onClick={(e) => { 
                          e.stopPropagation(); 
                          onDelete(); 
                        }}
                        variant="destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            
            {isClickable && onClick && (
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <div 
                  className={`${compact ? 'w-6 h-6' : 'w-8 h-8'} rounded-full flex items-center justify-center touch-target`}
                  style={{ backgroundColor: styles.hoverColor }}
                >
                  <ChevronRight className={`${compact ? 'w-3 h-3' : 'w-4 h-4'}`} style={{ color: styles.accentColor }} />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main content row with icon, title, and percentage */}
        <div className={`flex items-start ${compact ? 'gap-2' : 'gap-3 sm:gap-4'} ${compact ? 'mb-2' : 'mb-3'}`}>
          {/* Icon */}
          {icon && (
            <div 
              className={`${compact ? 'w-8 h-8' : 'w-10 h-10 sm:w-12 sm:h-12'} rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm`}
              style={{ 
                backgroundColor: iconBgColor || (color ? `${color}20` : `${styles.accentColor}20`)
              }}
            >
              <div style={{ color: color || styles.accentColor }}>
                {icon}
              </div>
            </div>
          )}

          {/* Title and Description - NO Tailwind typography classes */}
          <div className="flex-1 min-w-0">
            <h3 className={`text-white ${compact ? 'mb-0.5' : 'mb-1'} break-words`} style={{ 
              color: 'var(--aurum-text-primary)',
              fontSize: compact ? '0.95rem' : undefined,
              lineHeight: compact ? '1.3' : undefined
            }}>
              {title}
            </h3>
            {description && (
              <p className="break-words" style={{ 
                color: 'var(--aurum-text-secondary)',
                fontSize: compact ? '0.8rem' : undefined,
                lineHeight: compact ? '1.4' : undefined
              }}>
                {description}
              </p>
            )}
          </div>
          
          {/* Percentage section */}
          {(healthScore !== undefined || progress !== undefined) && (
            <div className={`text-right flex-shrink-0 ${compact ? 'min-w-[50px] pl-2' : 'min-w-[70px] sm:min-w-[90px] pl-3 sm:pl-4'}`}>
              <div 
                className={`font-bold ${compact ? 'mb-0.5' : 'mb-1'}`} 
                style={{ 
                  color: color || styles.accentColor,
                  fontSize: compact ? '1.1rem' : '1.5rem',
                  lineHeight: '1.2'
                }}
              >
                {Math.round(displayProgress)}%
              </div>
              <div 
                className="uppercase tracking-wide"
                style={{ 
                  color: 'var(--aurum-text-muted)',
                  fontSize: compact ? '0.65rem' : '0.75rem',
                  fontWeight: '500'
                }}
              >
                Progress
              </div>
            </div>
          )}
        </div>

        {/* Progress bar */}
        {(healthScore !== undefined || progress !== undefined) && (
          <div className={compact ? 'mb-2' : 'mb-4'}>
            <Progress 
              value={displayProgress} 
              className={`${compact ? 'h-1.5' : 'h-2'} bg-white/10`} 
              style={{
                '--progress-foreground': color || styles.accentColor
              } as React.CSSProperties}
            />
          </div>
        )}

        {/* Metrics section */}
        {metrics.length > 0 && (
          <div className={`grid ${compact ? 'gap-2 mb-2' : 'gap-3 mb-4'} ${metrics.length === 2 ? 'grid-cols-2' : metrics.length === 3 ? 'grid-cols-3' : metrics.length === 4 ? 'grid-cols-2 sm:grid-cols-4' : 'grid-cols-1'}`}>
            {metrics.map((metric, index) => (
              <div key={index} className={`flex items-center ${compact ? 'space-x-1 p-1.5' : 'space-x-2 p-2'} rounded-lg bg-white/5 border border-white/10`}>
                {metric.icon && (
                  <div 
                    className="flex-shrink-0 opacity-80"
                    style={{ color: metric.color || styles.accentColor }}
                  >
                    <div className={compact ? 'scale-75' : ''}>
                      {metric.icon}
                    </div>
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <div 
                    className="font-semibold break-words"
                    style={{ 
                      color: 'var(--aurum-text-primary)',
                      fontSize: compact ? '0.75rem' : '0.875rem'
                    }}
                  >
                    {metric.value}
                  </div>
                  <div 
                    className="break-words"
                    style={{ 
                      color: 'var(--aurum-text-muted)',
                      fontSize: compact ? '0.65rem' : '0.75rem'
                    }}
                  >
                    {metric.label}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Direct Action Buttons */}
      {showDirectActions && (onViewChildren || onEdit) && (
        <div className={`border-t border-white/10 bg-white/5 ${compact ? 'px-3 py-3' : 'px-4 sm:px-6 py-4'} flex items-center justify-between`}>
          {onViewChildren && (
            <Button
              variant="ghost"
              size="sm"
              className="text-[#B8BCC8] hover:text-white hover:bg-white/10 transition-all duration-200"
              onClick={(e) => {
                e.stopPropagation();
                console.log('🎯 View children button clicked');
                onViewChildren();
              }}
            >
              {level === 'pillar' ? 'View Areas' : 
               level === 'area' ? 'View Projects' : 
               level === 'project' ? 'View Tasks' : 'View Items'}
            </Button>
          )}
          {onEdit && (
            <Button
              variant="ghost"
              size="sm"
              className="text-[#B8BCC8] hover:text-white hover:bg-white/10 transition-all duration-200"
              onClick={(e) => {
                e.stopPropagation();
                console.log('🎯 Direct edit button clicked');
                onEdit();
              }}
            >
              Edit
            </Button>
          )}
        </div>
      )}

      {/* Sub-items section - Not clickable as main card */}
      {(subItems.length > 0 || children) && (
        <div className={`border-t border-white/10 bg-white/5 ${compact ? 'px-3 py-2' : 'px-4 sm:px-6 py-4'}`}>
          {/* Sub-items with clickable individual items */}
          {subItems.length > 0 && (
            <>
              <div className="flex items-center justify-between mb-3">
                <h4 
                  className="font-semibold uppercase tracking-wide"
                  style={{ 
                    color: 'var(--aurum-text-secondary)',
                    fontSize: '0.875rem'
                  }}
                >
                  {subItemsTitle || `${level === 'pillar' ? 'Focus Areas' : level === 'area' ? 'Projects' : level === 'project' ? 'Tasks' : 'Items'}`}
                </h4>
                <span 
                  className="bg-white/10 px-2 py-1 rounded-full"
                  style={{ 
                    color: 'var(--aurum-text-muted)',
                    fontSize: '0.75rem'
                  }}
                >
                  {subItems.length > 10 ? '10+' : subItems.length}
                </span>
              </div>
              <div className={`${compact ? 'space-y-1 max-h-24' : 'space-y-2 max-h-36'} overflow-y-auto hierarchy-card-scroll`}>
                {subItems.slice(0, 10).map((item, index) => {
                  const borderClass = level === 'pillar' ? 'hierarchy-area' : level === 'area' ? 'hierarchy-project' : 'hierarchy-task';
                  const itemProgress = item.progress ?? item.healthScore ?? 0;
                  const itemColor = level === 'pillar' ? '#3B82F6' : level === 'area' ? '#10B981' : '#8B5CF6';
                  
                  return (
                    <motion.div 
                      key={item.id}
                      className={`${borderClass} px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all cursor-pointer group border border-white/10 hover:border-opacity-30`}
                      onClick={(e) => {
                        e.stopPropagation();
                        item.onClick();
                      }}
                      whileHover={{ scale: 1.01, x: 2 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center justify-between">
                        <span 
                          className="break-words flex-1 group-hover:text-opacity-90 pr-2"
                          style={{ 
                            color: 'var(--aurum-text-primary)',
                            fontSize: '0.875rem'
                          }}
                        >
                          {item.name}
                        </span>
                        <div className="flex items-center space-x-2 ml-2 flex-shrink-0">
                          <span 
                            className="font-medium px-2 py-1 rounded-full bg-white/10"
                            style={{ 
                              color: itemColor,
                              fontSize: '0.75rem'
                            }}
                          >
                            {Math.round(itemProgress)}%
                          </span>
                          <ChevronRight 
                            className="w-3 h-3 opacity-0 group-hover:opacity-70 transition-opacity" 
                            style={{ color: itemColor }}
                          />
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
                {subItems.length > 10 && (
                  <div className="text-center pt-2 border-t border-white/10">
                    <span 
                      style={{ 
                        color: 'var(--aurum-text-muted)',
                        fontSize: '0.75rem'
                      }}
                    >
                      +{subItems.length - 10} more {level === 'pillar' ? 'areas' : level === 'area' ? 'projects' : 'items'}
                    </span>
                  </div>
                )}
              </div>
            </>
          )}
          
          {/* Legacy children support */}
          {children && (
            <div className="hierarchy-card-scroll border-t border-white/10 pt-4">
              {children}
            </div>
          )}
        </div>
      )}
    </Card>
  );

  if (isClickable && onClick) {
    return (
      <motion.div
        whileHover={{ scale: 1.02, y: -4 }}
        whileTap={{ scale: 0.98 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="cursor-pointer"
        onClick={onClick}
      >
        {cardContent}
      </motion.div>
    );
  }

  return cardContent;
}