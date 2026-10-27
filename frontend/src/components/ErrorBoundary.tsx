import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error caught by ErrorBoundary:', error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="card-surface p-6 rounded-xl border border-rose-500/20 bg-rose-950/10 space-y-4 my-4">
          <div className="flex items-center space-x-3 text-rose-400">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <h3 className="font-semibold text-sm">
              {this.props.fallbackTitle || 'A rendering error occurred in this section'}
            </h3>
          </div>
          <p className="text-xs text-slate-300 font-mono bg-black/40 p-3 rounded border border-white/5 overflow-x-auto">
            {this.state.error?.message || 'Unknown runtime error'}
          </p>
          <button
            onClick={this.handleReset}
            className="flex items-center space-x-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded text-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
