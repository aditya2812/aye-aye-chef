# Fix for "Always Returns Pineapple" Issue

## Problem
The ingredient detection is always returning "pineapple" instead of actually detecting the ingredients in the photo.

## Root Cause Analysis
1. **Database Issues**: The database tables may not be properly initialized
2. **User Management**: Users aren't being created in the database when they sign up
3. **Fallback Logic**: The app has hardcoded fallbacks that default to "pineapple"
4. **API Flow**: The detection flow may be failing silently

## Solutions Applied

### 1. Fixed API Service
- Removed duplicate `getScan` method in `mobile-app/src/services/api.js`

### 2. Updated Database Schema
- Created simplified `scripts/init-database.sql` for easier setup
- Removed strict foreign key constraints that could cause failures
- Made user creation more flexible

### 3. Improved Lambda Functions
- Updated `start-scan` Lambda to automatically create users if they don't exist
- Better error handling and logging

### 4. Fixed Fallback Logic
- Changed hardcoded "pineapple" fallback to generic "unknown food item"
- Better debugging information in the mobile app

## Next Steps to Deploy the Fix

### 1. Update the Database
```bash
# Connect to your Aurora database and run:
psql -h your-aurora-endpoint -U postgres -d ayeaye -f scripts/init-database.sql
```

### 2. Redeploy the Lambda Functions
```bash
npm run deploy
```

### 3. Test the Fix
1. Open the mobile app
2. Take a photo of any fruit or vegetable (not pineapple!)
3. Check the console logs for debugging information
4. Verify that real AI detection is working

### 4. Verify AWS Permissions
Make sure the Lambda functions have these permissions:
- `rekognition:DetectLabels` for the detect-ingredients function
- `s3:GetObject` for reading uploaded images
- `rds-data:ExecuteStatement` for database access

## Expected Behavior After Fix
- Photos of apples should detect "apple"
- Photos of bananas should detect "banana"  
- Photos of carrots should detect "carrot"
- Only fallback to "unknown food item" if detection truly fails

## Debugging Tips
- Check CloudWatch logs for the Lambda functions
- Use the "Test API" button in the mobile app to verify connectivity
- Look for console logs in the mobile app for detailed error messages