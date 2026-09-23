import React from 'react';

// NEW CONCEPT: Error Boundary
// What it is: A special React class component that acts like a "catch" block for rendering errors.
// Why we use it: If any component inside this boundary crashes (e.g. throws a JavaScript error during render),
// the Error Boundary catches it and displays a fallback UI instead of unmounting the entire application (the "black screen").
// What it does: It implements getDerivedStateFromError and componentDidCatch lifecycle methods.
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] bg-bg border border-red/20 rounded-2xl p-8 m-8 shadow-lg">
          <h2 className="text-2xl font-bold text-red mb-4">Something went wrong.</h2>
          <p className="text-text2 mb-6">A component crashed while trying to render. The error has been contained.</p>
          <div className="bg-bg3 text-text3 text-sm p-4 rounded-lg w-full max-w-2xl overflow-auto font-mono text-left mb-6">
            {this.state.error?.toString()}
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-accent text-white px-6 py-2 rounded-lg font-medium hover:bg-[#5b4cdb] transition-colors"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}
