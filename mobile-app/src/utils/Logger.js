// Production-safe logging utility
const isDevelopment = __DEV__ || process.env.NODE_ENV === 'development';

export const Logger = {
  // Only log in development
  debug: (message, ...args) => {
    if (isDevelopment) {
      console.log('[DEBUG]', message, ...args);
    }
  },
  
  info: (message, ...args) => {
    if (isDevelopment) {
      console.info('[INFO]', message, ...args);
    }
  },
  
  warn: (message, ...args) => {
    if (isDevelopment) {
      console.warn('[WARN]', message, ...args);
    }
  },
  
  error: (message, ...args) => {
    // Always log errors, but sanitize sensitive data
    const sanitizedArgs = args.map(arg => {
      if (typeof arg === 'object' && arg !== null) {
        return sanitizeObject(arg);
      }
      return arg;
    });
    console.error('[ERROR]', message, ...sanitizedArgs);
  }
};

// Sanitize objects to remove sensitive data
function sanitizeObject(obj) {
  const sensitiveKeys = ['token', 'password', 'secret', 'key', 'auth', 'jwt'];
  const sanitized = { ...obj };
  
  for (const key in sanitized) {
    if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
      sanitized[key] = '[REDACTED]';
    }
  }
  
  return sanitized;
}

export default Logger;
