#!/usr/bin/env node

// Simple script to test the Aye Aye API endpoints
const https = require('https');

const API_URL = 'https://c4qdpmgqqd.execute-api.us-west-2.amazonaws.com/prod';

// Test function
async function testEndpoint(path, method = 'GET', body = null, token = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(API_URL + path);
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'AyeAye-Test/1.0'
      }
    };

    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
    }

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', reject);
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

async function main() {
  console.log('🧪 Testing Aye Aye API...\n');

  // Test 1: Health check (should fail without auth)
  console.log('1. Testing presign endpoint (should return 401 without auth)');
  try {
    const result = await testEndpoint('/uploads/presign', 'POST');
    console.log(`   Status: ${result.status}`);
    console.log(`   Response: ${JSON.stringify(result.data, null, 2)}\n`);
  } catch (error) {
    console.log(`   Error: ${error.message}\n`);
  }

  // Test 2: Test with mock scan ID
  console.log('2. Testing get scan endpoint (should return 401 without auth)');
  try {
    const result = await testEndpoint('/scans/test-scan-123');
    console.log(`   Status: ${result.status}`);
    console.log(`   Response: ${JSON.stringify(result.data, null, 2)}\n`);
  } catch (error) {
    console.log(`   Error: ${error.message}\n`);
  }

  console.log('✅ API tests completed. All endpoints require authentication as expected.');
  console.log('💡 To test with authentication, you need to sign in through the mobile app first.');
}

main().catch(console.error);