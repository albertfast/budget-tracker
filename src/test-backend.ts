// Simple test file to verify backend services work
import ApiService from '../src/backend/services/apiService';

async function testApiService() {
  console.log('🧪 Testing SmartBudget Backend Services...');
  
  try {
    // Test configuration
    console.log('1. Testing configuration...');
    const configValidation = await ApiService.validateConfiguration();
    console.log('Config validation:', configValidation);
    
    // Test health check
    console.log('2. Testing health check...');
    const healthCheck = await ApiService.checkHealth();
    console.log('Health check:', healthCheck);
    
    console.log('✅ All tests completed successfully!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Export for use in app
export { testApiService };