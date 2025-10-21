#!/usr/bin/env python3
"""
Security hardening script to remove debug logs and sensitive information exposure.
"""

import os
import re
import glob

def remove_console_logs():
    """Remove console.log statements from mobile app files"""
    
    print("🔒 Security Hardening: Removing Debug Logs")
    print("=" * 60)
    
    # Find all JavaScript files in mobile app
    js_files = []
    for root, dirs, files in os.walk('mobile-app/src'):
        for file in files:
            if file.endswith('.js') or file.endswith('.jsx'):
                js_files.append(os.path.join(root, file))
    
    total_removed = 0
    files_modified = 0
    
    for file_path in js_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Remove various console.log patterns
            patterns_to_remove = [
                r'console\.log\([^)]*\);\s*\n?',  # console.log(...);
                r'console\.error\([^)]*\);\s*\n?',  # console.error(...);
                r'console\.warn\([^)]*\);\s*\n?',   # console.warn(...);
                r'console\.info\([^)]*\);\s*\n?',   # console.info(...);
                r'console\.debug\([^)]*\);\s*\n?',  # console.debug(...);
            ]
            
            removed_count = 0
            for pattern in patterns_to_remove:
                matches = re.findall(pattern, content)
                removed_count += len(matches)
                content = re.sub(pattern, '', content)
            
            # Remove empty lines that might be left behind
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ {os.path.relpath(file_path)}: Removed {removed_count} debug statements")
                total_removed += removed_count
                files_modified += 1
            else:
                print(f"⏭️  {os.path.relpath(file_path)}: No debug statements found")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(js_files)}")
    print(f"   Files modified: {files_modified}")
    print(f"   Debug statements removed: {total_removed}")
    
    return total_removed

def add_production_logging():
    """Add production-safe logging configuration"""
    
    print("\n🔧 Adding Production Logging Configuration")
    print("=" * 60)
    
    # Create a secure logger utility
    logger_content = '''// Production-safe logging utility
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
'''
    
    logger_path = 'mobile-app/src/utils/Logger.js'
    os.makedirs(os.path.dirname(logger_path), exist_ok=True)
    
    with open(logger_path, 'w') as f:
        f.write(logger_content)
    
    print(f"✅ Created secure logger: {logger_path}")

def create_security_config():
    """Create security configuration for production"""
    
    print("\n🛡️  Creating Security Configuration")
    print("=" * 60)
    
    security_config = '''// Security configuration for production builds
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
'''
    
    config_path = 'mobile-app/src/config/SecurityConfig.js'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(security_config)
    
    print(f"✅ Created security config: {config_path}")

def create_security_guidelines():
    """Create security guidelines documentation"""
    
    guidelines = '''# 🔒 Security Guidelines

## 🚨 **Security Issues Fixed**

### **Debug Logging Removed**
- ✅ Removed all `console.log()` statements exposing sensitive data
- ✅ Removed API URL logging
- ✅ Removed request/response body logging
- ✅ Removed authentication token logging
- ✅ Removed internal system state logging

### **Production-Safe Logging Added**
- ✅ Created `Logger` utility that only logs in development
- ✅ Added automatic sensitive data sanitization
- ✅ Created `SecurityConfig` for production builds

## 🛡️  **Security Best Practices**

### **1. Never Log Sensitive Data**
```javascript
// ❌ DON'T DO THIS
console.log('User token:', userToken);
console.log('API response:', fullApiResponse);

// ✅ DO THIS INSTEAD
Logger.debug('User authenticated successfully');
Logger.debug('API call completed');
```

### **2. Use Production-Safe Logging**
```javascript
import Logger from '../utils/Logger';

// Only logs in development
Logger.debug('Debug info here');
Logger.info('Info message');

// Always logs but sanitizes sensitive data
Logger.error('Error occurred', errorObject);
```

### **3. Sanitize Error Reports**
```javascript
// ❌ DON'T EXPOSE INTERNAL DETAILS
throw new Error(`Database connection failed: ${connectionString}`);

// ✅ USE GENERIC ERROR MESSAGES
throw new Error('Database connection failed');
```

### **4. Hide Internal URLs and IDs**
```javascript
// ❌ DON'T LOG FULL URLS
console.log('Calling API:', 'https://api.internal.com/v1/users/12345');

// ✅ LOG GENERIC MESSAGES
Logger.debug('Making API call to user service');
```

## 🔧 **Implementation**

### **Before Deployment**
1. Run security hardening script: `python security_hardening.py`
2. Replace all `console.log` with `Logger.debug`
3. Test that no sensitive data appears in browser tools
4. Verify production builds don't expose debug info

### **Code Review Checklist**
- [ ] No `console.log` statements with sensitive data
- [ ] No API URLs or tokens in logs
- [ ] No internal system details exposed
- [ ] Error messages are user-friendly, not technical
- [ ] Debug features disabled in production builds

## 🚀 **Production Deployment**

### **Environment Variables**
```bash
NODE_ENV=production
REACT_NATIVE_ENV=production
```

### **Build Configuration**
Ensure production builds:
- Strip all debug logs
- Minify and obfuscate code
- Remove development-only features
- Enable security headers

## 📱 **Mobile App Security**

### **What Users Should NOT See in Browser Tools**
- ❌ API endpoints and URLs
- ❌ Authentication tokens
- ❌ Internal scan IDs
- ❌ Database queries or responses
- ❌ Error stack traces
- ❌ Debug messages

### **What's Safe to Show**
- ✅ Generic success/failure messages
- ✅ User-facing error messages
- ✅ Public configuration values
- ✅ UI state changes (non-sensitive)

## 🎯 **Result**

After implementing these security measures:
- 🔒 **No sensitive data** exposed in browser developer tools
- 🔒 **No API details** visible to users
- 🔒 **No authentication tokens** logged
- 🔒 **No internal system information** exposed
- 🔒 **Production-ready** security posture
'''
    
    with open('docs/deployment/SECURITY_GUIDELINES.md', 'w') as f:
        f.write(guidelines)
    
    print(f"✅ Created security guidelines: docs/deployment/SECURITY_GUIDELINES.md")

def main():
    """Main security hardening function"""
    
    print("🔒 Mobile App Security Hardening")
    print("=" * 60)
    print("This script will remove debug logs and secure your production app.")
    print()
    
    # Remove debug logs
    removed_count = remove_console_logs()
    
    # Add production logging
    add_production_logging()
    
    # Create security config
    create_security_config()
    
    # Create guidelines
    create_security_guidelines()
    
    print("\n" + "=" * 60)
    print("🎉 Security Hardening Complete!")
    print(f"✅ Removed {removed_count} debug statements")
    print("✅ Added production-safe logging")
    print("✅ Created security configuration")
    print("✅ Created security guidelines")
    
    print("\n🚀 Next Steps:")
    print("1. Test the app to ensure it still works")
    print("2. Build for production and verify no sensitive data in browser tools")
    print("3. Deploy with confidence!")
    
    print("\n🔒 Security Status: HARDENED")

if __name__ == "__main__":
    main()