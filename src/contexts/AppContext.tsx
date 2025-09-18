import { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { AppState, SectionType, User, Notification } from '../types/app';

interface AppContextType {
  state: AppState;
  login: (user: User) => void;
  logout: () => void;
  setActiveSection: (section: SectionType) => void;
  openNotifications: () => void;
  closeNotifications: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

type AppAction = 
  | { type: 'LOGIN'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'SET_ACTIVE_SECTION'; payload: SectionType }
  | { type: 'OPEN_NOTIFICATIONS' }
  | { type: 'CLOSE_NOTIFICATIONS' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'HYDRATE_STATE'; payload: Partial<AppState> };

const initialState: AppState = {
  isAuthenticated: false,
  user: null,
  activeSection: 'dashboard',
  isNotificationsOpen: false,
  isLoading: false,
  error: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'LOGIN':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        error: null,
      };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        activeSection: 'dashboard',
        isNotificationsOpen: false,
      };
    case 'SET_ACTIVE_SECTION':
      return {
        ...state,
        activeSection: action.payload,
      };
    case 'OPEN_NOTIFICATIONS':
      return {
        ...state,
        isNotificationsOpen: true,
      };
    case 'CLOSE_NOTIFICATIONS':
      return {
        ...state,
        isNotificationsOpen: false,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'HYDRATE_STATE':
      return {
        ...state,
        ...action.payload,
      };
    default:
      return state;
  }
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Persist state to localStorage
  useEffect(() => {
    const savedState = localStorage.getItem('aurum-life-state');
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState);
        dispatch({ type: 'HYDRATE_STATE', payload: parsedState });
      } catch (error) {
        console.error('Failed to parse saved state:', error);
      }
    }
  }, []);

  // Save state changes to localStorage
  useEffect(() => {
    const stateToSave = {
      isAuthenticated: state.isAuthenticated,
      user: state.user,
      activeSection: state.activeSection,
    };
    localStorage.setItem('aurum-life-state', JSON.stringify(stateToSave));
  }, [state.isAuthenticated, state.user, state.activeSection]);

  const contextValue: AppContextType = {
    state,
    login: (user: User) => dispatch({ type: 'LOGIN', payload: user }),
    logout: () => {
      localStorage.removeItem('aurum-life-state');
      dispatch({ type: 'LOGOUT' });
    },
    setActiveSection: (section: SectionType) => 
      dispatch({ type: 'SET_ACTIVE_SECTION', payload: section }),
    openNotifications: () => dispatch({ type: 'OPEN_NOTIFICATIONS' }),
    closeNotifications: () => dispatch({ type: 'CLOSE_NOTIFICATIONS' }),
    setLoading: (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }),
    setError: (error: string | null) => dispatch({ type: 'SET_ERROR', payload: error }),
    clearError: () => dispatch({ type: 'CLEAR_ERROR' }),
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}