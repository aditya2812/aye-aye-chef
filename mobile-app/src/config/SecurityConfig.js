// Security configuration for production builds
export const SecurityConfig = {
  // Disable debug features in production
  enableDebugLogs: __DEV__,
  enableNetworkLogging: __DEV__,
  enablePerformanceLogging: __DEV__,
  
  // API security settings
  api: {
    // Don't log full URLs in production
    logFullUrls: __DEV__,
    // Don't log request/response bodies in production
    logRequestBodies: __DEV__,
    logResponseBodies: __DEV__,
    // Don't log headers in production (may contain tokens)
    logHeaders: false,
  },
  
  // Error reporting settings
  errorReporting: {
    // Sanitize error data before reporting
    sanitizeErrors: !__DEV__,
    // Don't include stack traces in production error reports
    includeStackTrace: __DEV__,
  }
};

export default SecurityConfig;
