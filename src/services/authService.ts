// Simple auth service for handling tokens
// In a real app, this would integrate with your authentication system

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

  getCurrentUser(): { id: string } | null {
    if (!this.authToken) return null;
    
    // Extract user ID from mock token for demo purposes
    // In a real app, this would decode the JWT token
    const match = this.authToken.match(/mock-jwt-token-(.+?)-\d+/);
    if (match) {
      return { id: match[1] };
    }
    
    return { id: 'demo-user' };
  }

  // Mock authentication for demo purposes
  mockLogin(userId: string = 'demo-user'): string {
    // In a real app, this would call your auth API
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