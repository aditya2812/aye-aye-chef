#!/usr/bin/env node

// Test script to debug the create recipe API
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
  console.log('🧪 Testing Create Recipe API...\n');

  // Test create recipe endpoint without auth (should return 401)
  console.log('1. Testing create recipe without auth (should return 401)');
  try {
    const result = await testEndpoint('/recipes', 'POST', { scan_id: 'test', servings: 2 });
    console.log(`   Status: ${result.status} ${result.status === 401 ? '✅' : '❌'}`);
    console.log(`   Response: ${JSON.stringify(result.data, null, 2)}\n`);
  } catch (error) {
    console.log(`   Error: ${error.message}\n`);
  }

  console.log('💡 To test with real data:');
  console.log('   1. Sign in through the mobile app');
  console.log('   2. Complete a scan and confirm ingredients');
  console.log('   3. Use the JWT token and real scan_id');
  console.log('   4. Check browser console for detailed error messages');
  
  console.log('\n🔍 Common issues:');
  console.log('   - Scan status not "confirmed"');
  console.log('   - No confirmed ingredients in database');
  console.log('   - Invalid scan_id or user_id mismatch');
  console.log('   - Database connection issues');
}

main().catch(console.error);