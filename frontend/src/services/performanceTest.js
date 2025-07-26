/**
 * COMPREHENSIVE PERFORMANCE TEST - Test all endpoints systematically
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// Test runner with detailed logging
class PerformanceTest {
  constructor() {
    this.results = [];
  }
  
  async testEndpoint(name, url, options = {}) {
    const startTime = Date.now();
    console.log(`🧪 Testing ${name}...`);
    
    try {
      const fetchOptions = {
        method: options.method || 'GET',
        headers: { 'Content-Type': 'application/json', ...options.headers },
        timeout: 10000
      };
      
      if (options.body) {
        fetchOptions.body = options.body;
      }
      
      const response = await fetch(`${API_BASE}${url}`, fetchOptions);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${name}: ${response.status} in ${duration}ms`);
        this.results.push({ name, status: 'SUCCESS', duration, statusCode: response.status });
        return data;
      } else {
        console.log(`❌ ${name}: ${response.status} in ${duration}ms`);
        this.results.push({ name, status: 'ERROR', duration, statusCode: response.status });
        return null;
      }
    } catch (error) {
      const endTime = Date.now();
      const duration = endTime - startTime;
      console.log(`💥 ${name}: ${error.message} in ${duration}ms`);
      this.results.push({ name, status: 'TIMEOUT/ERROR', duration, error: error.message });
      return null;
    }
  }
  
  async runAllTests() {
    console.log('🚀 Starting comprehensive performance tests...');
    
    // Test 1: Health check (should be fast)
    await this.testEndpoint('Health Check', '/api/health');
    
    // Test 2: Login (get auth token)
    const loginData = await this.testEndpoint('Login', '/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: 'marc.alleyne@aurumtechnologyltd.com',
        password: 'password123'
      })
    });
    
    if (!loginData?.access_token) {
      console.log('❌ Cannot continue - login failed');
      return this.results;
    }
    
    const authHeaders = { 'Authorization': `Bearer ${loginData.access_token}` };
    
    // Test 3: Current user (should be fast)
    await this.testEndpoint('Current User', '/api/auth/me', authHeaders);
    
    // Test 4: Dashboard (was slow - now optimized)
    await this.testEndpoint('Dashboard', '/api/dashboard', authHeaders);
    
    // Test 5: AI Coach (was slow - now optimized)
    await this.testEndpoint('AI Coach', '/api/ai_coach/today', authHeaders);
    
    // Test 6: Areas (was slow - now optimized)
    await this.testEndpoint('Areas', '/api/areas?include_projects=true&include_archived=false', authHeaders);
    
    // Test 7: Projects (for comparison)
    await this.testEndpoint('Projects', '/api/projects', authHeaders);
    
    // Test 8: Insights (was slow)
    await this.testEndpoint('Insights', '/api/insights?date_range=all_time', authHeaders);
    
    console.log('\n📊 Test Results Summary:');
    this.results.forEach(result => {
      const status = result.status === 'SUCCESS' ? '✅' : '❌';
      console.log(`${status} ${result.name}: ${result.duration}ms (${result.status})`);
    });
    
    // Calculate performance metrics
    const successfulTests = this.results.filter(r => r.status === 'SUCCESS');
    const avgTime = successfulTests.reduce((sum, r) => sum + r.duration, 0) / successfulTests.length;
    const slowTests = successfulTests.filter(r => r.duration > 2000);
    
    console.log(`\n📈 Performance Metrics:`);
    console.log(`- Successful tests: ${successfulTests.length}/${this.results.length}`);
    console.log(`- Average response time: ${avgTime.toFixed(0)}ms`);
    console.log(`- Slow tests (>2s): ${slowTests.length}`);
    
    if (slowTests.length > 0) {
      console.log(`🐌 Slow endpoints that need optimization:`);
      slowTests.forEach(test => {
        console.log(`   - ${test.name}: ${test.duration}ms`);
      });
    }
    
    return this.results;
  }
}

// Global test runner for browser console
window.runPerformanceTests = async () => {
  const tester = new PerformanceTest();
  return await tester.runAllTests();
};

// Auto-run tests when loaded
if (typeof window !== 'undefined') {
  console.log('🧪 Performance test module loaded. Run window.runPerformanceTests() to start.');
}