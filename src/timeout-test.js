#!/usr/bin/env node

/**
 * Simple timeout test to verify the fixes work
 * Tests app startup without hanging operations
 */

const { spawn } = require('child_process');
const http = require('http');

console.log('🔍 Testing timeout fixes...\n');

// Test 1: Check if dev server starts without hanging
function testDevServerStart() {
  return new Promise((resolve, reject) => {
    console.log('📋 Test 1: Starting dev server...');
    
    const server = spawn('npm', ['run', 'dev'], {
      stdio: 'pipe',
      detached: false
    });

    let hasStarted = false;
    
    // Listen for server ready
    server.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('📢 Server output:', output.trim());
      
      if (output.includes('Local:') || output.includes('localhost:3000') || output.includes('ready')) {
        hasStarted = true;
        console.log('✅ Dev server started successfully');
        server.kill('SIGTERM');
        resolve(true);
      }
    });

    server.stderr.on('data', (data) => {
      const error = data.toString();
      console.log('⚠️ Server error:', error.trim());
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!hasStarted) {
        console.log('❌ Dev server failed to start within 30 seconds');
        server.kill('SIGTERM');
        reject(new Error('Dev server startup timeout'));
      }
    }, 30000);

    server.on('error', (error) => {
      console.log('❌ Server spawn error:', error);
      reject(error);
    });
  });
}

// Test 2: Check if app page loads without hanging
function testPageLoad() {
  return new Promise((resolve, reject) => {
    console.log('\n📋 Test 2: Testing page load...');
    
    const startTime = Date.now();
    
    const req = http.get('http://localhost:3000', (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const loadTime = Date.now() - startTime;
        console.log(`✅ Page loaded successfully in ${loadTime}ms`);
        
        if (data.includes('Aurum Life') || data.includes('root')) {
          console.log('✅ Page content looks correct');
          resolve(true);
        } else {
          console.log('⚠️ Page content may be incomplete');
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      console.log('❌ Page load error:', error.message);
      reject(error);
    });
    
    // Timeout after 10 seconds
    req.setTimeout(10000, () => {
      console.log('❌ Page load timeout after 10 seconds');
      req.destroy();
      reject(new Error('Page load timeout'));
    });
  });
}

// Test 3: Multiple rapid requests to check for getPage issues
function testRapidRequests() {
  return new Promise((resolve, reject) => {
    console.log('\n📋 Test 3: Testing rapid requests...');
    
    let completed = 0;
    let errors = 0;
    const totalRequests = 5;
    
    for (let i = 0; i < totalRequests; i++) {
      const req = http.get('http://localhost:3000', (res) => {
        completed++;
        res.on('data', () => {}); // Consume data
        res.on('end', () => {
          if (completed + errors === totalRequests) {
            if (errors === 0) {
              console.log(`✅ All ${totalRequests} rapid requests completed successfully`);
              resolve(true);
            } else {
              console.log(`⚠️ ${errors} out of ${totalRequests} requests failed`);
              resolve(false);
            }
          }
        });
      });
      
      req.on('error', () => {
        errors++;
        if (completed + errors === totalRequests) {
          console.log(`❌ ${errors} out of ${totalRequests} requests failed`);
          resolve(false);
        }
      });
      
      req.setTimeout(5000, () => {
        req.destroy();
        errors++;
      });
    }
  });
}

// Run all tests
async function runTimeoutTests() {
  try {
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                     🧪 TIMEOUT FIX TESTING                  ║
║              Verifying timeout error fixes work             ║
╚══════════════════════════════════════════════════════════════╝
`);

    // Test dev server start
    await testDevServerStart();
    
    // Wait a moment for server to stabilize
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test page load
    const pageLoadResult = await testPageLoad();
    
    // Test rapid requests
    const rapidRequestResult = await testRapidRequests();
    
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                     📊 TEST RESULTS                         ║
╚══════════════════════════════════════════════════════════════╝

✅ Dev Server Start: PASSED
${pageLoadResult ? '✅' : '❌'} Page Load: ${pageLoadResult ? 'PASSED' : 'FAILED'}
${rapidRequestResult ? '✅' : '❌'} Rapid Requests: ${rapidRequestResult ? 'PASSED' : 'FAILED'}

${pageLoadResult && rapidRequestResult ? 
  '🎉 All timeout fix tests PASSED! The getPage timeout errors should be resolved.' :
  '⚠️ Some tests failed. Check the logs above for details.'
}
`);

    process.exit(pageLoadResult && rapidRequestResult ? 0 : 1);
    
  } catch (error) {
    console.error(`
╔══════════════════════════════════════════════════════════════╗
║                      ❌ TEST FAILED                         ║
║                   ${error.message.padEnd(50)} ║
╚══════════════════════════════════════════════════════════════╝
`);
    process.exit(1);
  }
}

// Handle process signals
process.on('SIGINT', () => {
  console.log('\n🛑 Test interrupted by user');
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Test terminated');
  process.exit(1);
});

// Run the tests
if (require.main === module) {
  runTimeoutTests();
}

module.exports = { runTimeoutTests };