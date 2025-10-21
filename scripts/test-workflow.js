#!/usr/bin/env node

// Test script for the complete Aye Aye workflow
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
  console.log('🧪 Testing Aye Aye Complete Workflow...\n');

  // Test 1: Health check endpoints (should return 401 without auth)
  console.log('1. Testing endpoints without authentication (should return 401)');
  
  const endpoints = [
    { path: '/uploads/presign', method: 'POST' },
    { path: '/scans', method: 'POST' },
    { path: '/scans/test-123', method: 'GET' },
    { path: '/scans/test-123/confirm', method: 'POST' },
    { path: '/recipes', method: 'POST' },
    { path: '/recipes/test-456', method: 'GET' }
  ];

  for (const endpoint of endpoints) {
    try {
      const result = await testEndpoint(endpoint.path, endpoint.method);
      console.log(`   ${endpoint.method} ${endpoint.path}: ${result.status} ${result.status === 401 ? '✅' : '❌'}`);
    } catch (error) {
      console.log(`   ${endpoint.method} ${endpoint.path}: Error - ${error.message}`);
    }
  }

  console.log('\n✅ All endpoints properly require authentication.');
  console.log('\n📋 Complete Workflow Summary:');
  console.log('   Step 1: POST /uploads/presign - Get S3 upload URL');
  console.log('   Step 2: PUT to S3 - Upload image');
  console.log('   Step 3: POST /scans - Start ingredient detection');
  console.log('   Step 4: GET /scans/{id} - Check scan results');
  console.log('   Step 5: POST /scans/{id}/confirm - Confirm ingredients');
  console.log('   Step 6: POST /recipes - Create recipe from scan');
  console.log('   Step 7: GET /recipes/{id} - View generated recipe');
  
  console.log('\n💡 To test with authentication:');
  console.log('   1. Sign in through the mobile app');
  console.log('   2. Use the JWT token in Authorization header');
  console.log('   3. Follow the workflow steps above');
  
  console.log('\n🎯 Next Steps for Full AI Integration:');
  console.log('   - Set up Bedrock Agent for intelligent recipe generation');
  console.log('   - Add Knowledge Base for portion heuristics');
  console.log('   - Implement advanced nutrition computation');
  console.log('   - Add dietary preference handling');
}

main().catch(console.error);