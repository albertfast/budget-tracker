// Simple auth service for handling tokens
// In a real app, this would integrate with your authentication system
import { API_BASE_URL } from '../config';

class AuthService {
  private static instance: AuthService;
  private authToken: string | null = null;

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  isAuthenticated(): boolean {
    return this.authToken !== null;
  }

  // Real authentication using the seeded user
  async login(email: string = 'albertfast@gmail.com', password: string = 'abc123'): Promise<string> {
    // API_BASE_URL is now imported from config
    
    try {
      console.log('Logging in with:', email);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Login failed:', errorText);
        throw new Error(`Login failed: ${response.status}`);
      }

      const data = await response.json();
      const token = data.access_token;
      this.setAuthToken(token);
      console.log('Login successful, token set');
      return token;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  // Keep mockLogin for compatibility but warn
  mockLogin(userId: string = 'demo-user'): string {
    console.warn('Using mockLogin - this will likely fail with real backend!');
    const mockToken = `mock-jwt-token-${userId}-${Date.now()}`;
    this.setAuthToken(mockToken);
    return mockToken;
  }

  logout() {
    this.authToken = null;
  }
}

export const authService = AuthService.getInstance();

// Helper function for making authenticated API calls
export const makeAuthenticatedRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const authHeaders = authService.getAuthHeaders();
  
  const requestOptions: RequestInit = {
    ...options,
    headers: {
      ...authHeaders,
      ...options.headers,
    },
  };

  return fetch(url, requestOptions);
};

export default authService;