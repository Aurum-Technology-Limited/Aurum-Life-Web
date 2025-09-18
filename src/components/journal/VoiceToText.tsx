import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Square, Play, Pause, Volume2, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import CharacterLimitIndicator, { getCharacterLimitStatus } from '../shared/CharacterLimitIndicator';

interface VoiceToTextProps {
  onTextChange: (text: string) => void;
  initialText?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

type RecordingState = 'idle' | 'recording' | 'paused' | 'processing';

interface VoiceRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

export default function VoiceToText({
  onTextChange,
  initialText = '',
  placeholder = 'Click the microphone to start voice recording, or type your text here...',
  disabled = false,
  className = ''
}: VoiceToTextProps) {
  // Character limit for voice input (matches journal content limit)
  const MAX_CONTENT_LENGTH = 50000;
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [text, setText] = useState(initialText);
  const [isListening, setIsListening] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  const [confidence, setConfidence] = useState<number | null>(null);

  // Refs for voice recognition
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const intervalRef = useRef<number | null>(null);
  const animationRef = useRef<number | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  // Check for browser support
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !navigator.mediaDevices?.getUserMedia) {
      setIsSupported(false);
      setError('Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Initialize Speech Recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        
        if (result.isFinal) {
          finalTranscript += transcript + ' ';
          setConfidence(result[0].confidence);
        } else {
          interimTranscript += transcript;
        }
      }

      if (finalTranscript) {
        const potentialNewText = text + finalTranscript;
        // Apply character limit
        const newText = potentialNewText.length > MAX_CONTENT_LENGTH 
          ? potentialNewText.substring(0, MAX_CONTENT_LENGTH)
          : potentialNewText;
        setText(newText);
        onTextChange(newText);
        
        // Show warning if content was truncated
        if (potentialNewText.length > MAX_CONTENT_LENGTH) {
          setError(`Content limit reached (${MAX_CONTENT_LENGTH} characters). Additional speech will not be recorded.`);
        }
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
      
      let userFriendlyMessage = '';
      switch (event.error) {
        case 'not-allowed':
          userFriendlyMessage = 'Microphone access denied. Please enable microphone permissions and try again.';
          break;
        case 'no-speech':
          userFriendlyMessage = 'No speech detected. Please speak clearly into your microphone.';
          break;
        case 'audio-capture':
          userFriendlyMessage = 'Unable to capture audio. Please check your microphone connection.';
          break;
        case 'network':
          userFriendlyMessage = 'Network error occurred. Please check your internet connection.';
          break;
        case 'service-not-allowed':
          userFriendlyMessage = 'Speech recognition service is not available. Please try again later.';
          break;
        case 'bad-grammar':
          userFriendlyMessage = 'Speech recognition grammar error. Please try speaking more clearly.';
          break;
        case 'language-not-supported':
          userFriendlyMessage = 'Language not supported for speech recognition.';
          break;
        default:
          userFriendlyMessage = `Voice recognition error: ${event.error}. Please try again.`;
      }
      
      setError(userFriendlyMessage);
      setIsListening(false);
      setRecordingState('idle');
    };

    recognition.onend = () => {
      setIsListening(false);
      if (recordingState === 'recording') {
        // Restart if we're still supposed to be recording
        recognition.start();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [recordingState, text, onTextChange]);

  // Update text when initialText changes
  useEffect(() => {
    setText(initialText);
  }, [initialText]);

  // Audio level monitoring
  const startAudioMonitoring = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      analyser.fftSize = 256;
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      microphone.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const updateAudioLevel = () => {
        if (analyser && recordingState === 'recording') {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
          setAudioLevel(Math.min(100, (average / 255) * 100 * 3)); // Amplify for better visualization
          animationRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };

      updateAudioLevel();
    } catch (err: any) {
      console.error('Error accessing microphone:', err);
      
      if (err.name === 'NotAllowedError') {
        setError('Microphone access denied. Please allow microphone access and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('No microphone detected. Please connect a microphone and try again.');
      } else {
        setError('Unable to access microphone. Please check your device settings.');
      }
      
      setRecordingState('idle');
    }
  };

  const stopAudioMonitoring = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setAudioLevel(0);
  };

  const requestMicrophonePermission = async (): Promise<boolean> => {
    try {
      // First check if permissions API is available
      if ('permissions' in navigator) {
        const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        if (permissionStatus.state === 'denied') {
          setError('Microphone access is blocked. Please enable microphone permissions in your browser settings.');
          return false;
        }
      }

      // Try to get user media to request permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop the stream immediately as we just wanted to get permission
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (err: any) {
      console.error('Microphone permission error:', err);
      
      if (err.name === 'NotAllowedError') {
        setError('Microphone access denied. Please click the microphone icon in your browser\'s address bar and allow access.');
      } else if (err.name === 'NotFoundError') {
        setError('No microphone found. Please check that a microphone is connected.');
      } else if (err.name === 'NotSupportedError') {
        setError('Microphone access is not supported on this device.');
      } else {
        setError('Unable to access microphone. Please check your browser permissions.');
      }
      return false;
    }
  };

  const startRecording = async () => {
    if (!isSupported || disabled) return;

    try {
      setRecordingState('processing');
      setError(null);
      
      // First request microphone permission
      const hasPermission = await requestMicrophonePermission();
      if (!hasPermission) {
        setRecordingState('idle');
        return;
      }

      setRecordingState('recording');
      setRecordingTime(0);
      
      // Start audio monitoring
      await startAudioMonitoring();
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }

      // Start timer
      intervalRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
      setRecordingState('idle');
    }
  };

  const stopRecording = () => {
    setRecordingState('processing');
    setIsListening(false);

    // Stop speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    // Stop timer
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Stop audio monitoring
    stopAudioMonitoring();

    // Simulate processing time
    setTimeout(() => {
      setRecordingState('idle');
      setRecordingTime(0);
    }, 1000);
  };

  const pauseRecording = () => {
    setRecordingState('paused');
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    stopAudioMonitoring();
  };

  const resumeRecording = () => {
    setRecordingState('recording');
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
    startAudioMonitoring();
  };

  const handleTextChange = (newText: string) => {
    // Apply character limit for manual text input
    const truncatedText = newText.length > MAX_CONTENT_LENGTH 
      ? newText.substring(0, MAX_CONTENT_LENGTH)
      : newText;
    setText(truncatedText);
    onTextChange(truncatedText);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getRecordingIcon = () => {
    switch (recordingState) {
      case 'recording':
        return <Square className="w-4 h-4" />;
      case 'paused':
        return <Play className="w-4 h-4" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      default:
        return <Mic className="w-4 h-4" />;
    }
  };

  const getRecordingButtonClass = () => {
    if (disabled) return 'bg-muted text-muted-foreground cursor-not-allowed';
    
    switch (recordingState) {
      case 'recording':
        return 'bg-red-500 hover:bg-red-600 text-white animate-pulse';
      case 'paused':
        return 'bg-yellow-500 hover:bg-yellow-600 text-white';
      case 'processing':
        return 'bg-blue-500 text-white cursor-not-allowed';
      default:
        return 'bg-primary hover:bg-primary/90 text-primary-foreground';
    }
  };

  if (!isSupported) {
    return (
      <div className={`space-y-4 ${className}`}>
        <Alert className="border-destructive/50 text-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Voice recording is not supported in this browser. You can still type your text.
          </AlertDescription>
        </Alert>
        
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-muted-foreground">Content Editor</span>
          <CharacterLimitIndicator
            currentLength={text.length}
            maxLength={MAX_CONTENT_LENGTH}
            showProgress={true}
            showIcon={true}
            warningThreshold={80}
            dangerThreshold={95}
          />
        </div>
        
        <Textarea
          value={text}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className="min-h-[120px] glassmorphism-panel border-0"
          maxLength={MAX_CONTENT_LENGTH}
        />
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Voice Control Panel */}
      <div className="glassmorphism-panel p-4 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              onClick={
                recordingState === 'idle' ? startRecording :
                recordingState === 'recording' ? stopRecording :
                recordingState === 'paused' ? resumeRecording :
                undefined
              }
              disabled={disabled || recordingState === 'processing'}
              className={getRecordingButtonClass()}
            >
              {getRecordingIcon()}
              <span className="ml-2">
                {recordingState === 'idle' ? 'Start Recording' :
                 recordingState === 'recording' ? 'Stop' :
                 recordingState === 'paused' ? 'Resume' :
                 'Processing...'}
              </span>
            </Button>

            {recordingState === 'recording' && (
              <Button
                onClick={pauseRecording}
                variant="outline"
                className="glassmorphism-panel border-0"
              >
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </Button>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {recordingState !== 'idle' && (
              <Badge variant="secondary" className="glassmorphism-subtle">
                {formatTime(recordingTime)}
              </Badge>
            )}
            
            {confidence !== null && (
              <Badge 
                variant="outline" 
                className={`glassmorphism-subtle ${confidence > 0.8 ? 'border-green-500 text-green-500' : 
                  confidence > 0.6 ? 'border-yellow-500 text-yellow-500' : 
                  'border-red-500 text-red-500'}`}
              >
                {Math.round(confidence * 100)}% confident
              </Badge>
            )}
          </div>
        </div>

        {/* Audio Level Indicator */}
        {recordingState === 'recording' && (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-muted-foreground" />
              <div className="flex-1">
                <Progress 
                  value={audioLevel} 
                  className="h-2"
                />
              </div>
              <span className="text-xs text-muted-foreground w-8">
                {Math.round(audioLevel)}%
              </span>
            </div>
            {isListening && (
              <div className="flex items-center space-x-2 text-sm text-green-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>Listening...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="border-destructive/50 text-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <p>{error}</p>
              {error.includes('denied') || error.includes('blocked') && (
                <div className="text-xs text-muted-foreground">
                  <p><strong>To enable microphone access:</strong></p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>Click the microphone icon in your browser's address bar</li>
                    <li>Select "Allow" for microphone permissions</li>
                    <li>Refresh the page if needed</li>
                  </ul>
                </div>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Character Limit Display */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-muted-foreground">Content Editor</span>
        <CharacterLimitIndicator
          currentLength={text.length}
          maxLength={MAX_CONTENT_LENGTH}
          showProgress={true}
          showIcon={true}
          warningThreshold={80}
          dangerThreshold={95}
        />
      </div>

      {/* Text Editor */}
      <Textarea
        value={text}
        onChange={(e) => handleTextChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="min-h-[120px] glassmorphism-panel border-0"
        maxLength={MAX_CONTENT_LENGTH}
      />
    </div>
  );
}

// Type declarations for Speech Recognition API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
  
  interface SpeechRecognitionEvent extends Event {
    results: SpeechRecognitionResultList;
    resultIndex: number;
  }
  
  interface SpeechRecognitionErrorEvent extends Event {
    error: string;
    message?: string;
  }
}