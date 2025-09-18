import { useEffect, useState, useCallback } from 'react';

interface TouchState {
  isTouching: boolean;
  touchStart: { x: number; y: number } | null;
  touchCurrent: { x: number; y: number } | null;
  swipeDirection: 'left' | 'right' | 'up' | 'down' | null;
  swipeDistance: number;
}

interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number;
  velocity: number;
  duration: number;
}

interface TouchOptions {
  swipeThreshold?: number;
  velocityThreshold?: number;
  onSwipe?: (gesture: SwipeGesture) => void;
  preventDefault?: boolean;
}

export function useTouch(options: TouchOptions = {}) {
  const {
    swipeThreshold = 50,
    velocityThreshold = 0.3,
    onSwipe,
    preventDefault = false
  } = options;

  const [touchState, setTouchState] = useState<TouchState>({
    isTouching: false,
    touchStart: null,
    touchCurrent: null,
    swipeDirection: null,
    swipeDistance: 0
  });

  const [startTime, setStartTime] = useState<number>(0);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (preventDefault) {
      e.preventDefault();
    }

    const touch = e.touches[0];
    const point = { x: touch.clientX, y: touch.clientY };
    
    setTouchState(prev => ({
      ...prev,
      isTouching: true,
      touchStart: point,
      touchCurrent: point,
      swipeDirection: null,
      swipeDistance: 0
    }));
    
    setStartTime(Date.now());
  }, [preventDefault]);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (preventDefault) {
      e.preventDefault();
    }

    const touch = e.touches[0];
    const current = { x: touch.clientX, y: touch.clientY };

    setTouchState(prev => {
      if (!prev.touchStart) return prev;

      const deltaX = current.x - prev.touchStart.x;
      const deltaY = current.y - prev.touchStart.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      let direction: 'left' | 'right' | 'up' | 'down' | null = null;
      
      if (distance > 10) { // Minimum distance to determine direction
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          direction = deltaX > 0 ? 'right' : 'left';
        } else {
          direction = deltaY > 0 ? 'down' : 'up';
        }
      }

      return {
        ...prev,
        touchCurrent: current,
        swipeDirection: direction,
        swipeDistance: distance
      };
    });
  }, [preventDefault]);

  const handleTouchEnd = useCallback((e: TouchEvent) => {
    if (preventDefault) {
      e.preventDefault();
    }

    const endTime = Date.now();
    const duration = endTime - startTime;

    setTouchState(prev => {
      if (!prev.touchStart || !prev.touchCurrent) {
        return {
          ...prev,
          isTouching: false,
          touchStart: null,
          touchCurrent: null,
          swipeDirection: null,
          swipeDistance: 0
        };
      }

      const deltaX = prev.touchCurrent.x - prev.touchStart.x;
      const deltaY = prev.touchCurrent.y - prev.touchStart.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const velocity = distance / duration;

      if (distance >= swipeThreshold && velocity >= velocityThreshold && onSwipe) {
        const direction = Math.abs(deltaX) > Math.abs(deltaY)
          ? (deltaX > 0 ? 'right' : 'left')
          : (deltaY > 0 ? 'down' : 'up');

        onSwipe({
          direction,
          distance,
          velocity,
          duration
        });
      }

      return {
        ...prev,
        isTouching: false,
        touchStart: null,
        touchCurrent: null,
        swipeDirection: null,
        swipeDistance: 0
      };
    });
  }, [swipeThreshold, velocityThreshold, onSwipe, startTime]);

  const bindTouch = useCallback(() => ({
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,
  }), [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return {
    touchState,
    bindTouch,
    isSupported: 'ontouchstart' in window || navigator.maxTouchPoints > 0
  };
}

export function useHapticFeedback() {
  const vibrate = useCallback((pattern: number | number[] = 10) => {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  }, []);

  const lightImpact = useCallback(() => vibrate(10), [vibrate]);
  const mediumImpact = useCallback(() => vibrate(20), [vibrate]);
  const heavyImpact = useCallback(() => vibrate([20, 10, 20]), [vibrate]);
  const selectionChanged = useCallback(() => vibrate(5), [vibrate]);
  const notificationFeedback = useCallback(() => vibrate([100, 50, 100]), [vibrate]);

  return {
    vibrate,
    lightImpact,
    mediumImpact,
    heavyImpact,
    selectionChanged,
    notificationFeedback,
    isSupported: 'vibrate' in navigator
  };
}

export function useTouchOptimization() {
  const [isTouch, setIsTouch] = useState(false);
  const [touchSize, setTouchSize] = useState<'small' | 'medium' | 'large'>('medium');

  useEffect(() => {
    const checkTouch = () => {
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      setIsTouch(hasTouch);

      // Determine optimal touch target size based on device
      const screenWidth = window.innerWidth;
      if (screenWidth < 375) {
        setTouchSize('small');
      } else if (screenWidth > 768) {
        setTouchSize('large');
      } else {
        setTouchSize('medium');
      }
    };

    checkTouch();
    window.addEventListener('resize', checkTouch);
    return () => window.removeEventListener('resize', checkTouch);
  }, []);

  const getTouchTargetSize = useCallback(() => {
    switch (touchSize) {
      case 'small': return 'min-h-[40px] min-w-[40px]';
      case 'large': return 'min-h-[48px] min-w-[48px]';
      default: return 'min-h-[44px] min-w-[44px]';
    }
  }, [touchSize]);

  const getTouchPadding = useCallback(() => {
    switch (touchSize) {
      case 'small': return 'p-2';
      case 'large': return 'p-4';
      default: return 'p-3';
    }
  }, [touchSize]);

  return {
    isTouch,
    touchSize,
    getTouchTargetSize,
    getTouchPadding
  };
}