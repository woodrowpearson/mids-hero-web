// API service for communicating with the FastAPI backend
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Base API client configuration
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      throw new Error(
        `API request failed: ${response.status} ${response.statusText}`
      );
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

// Create API client instance
export const apiClient = new ApiClient(API_BASE_URL);

// Type definitions for API responses
export interface Archetype {
  id: number;
  name: string;
  description: string;
  primary_powersets: string[];
  secondary_powersets: string[];
  origins: string[];
}

export interface Powerset {
  id: number;
  name: string;
  description: string;
  archetype_id: number;
  powers: Power[];
}

export interface Power {
  id: number;
  name: string;
  description: string;
  level_available: number;
  powerset_id: number;
  prerequisites: number[];
  enhancement_categories: string[];
}

export interface Enhancement {
  id: number;
  name: string;
  description: string;
  category: string;
  set_name?: string;
  bonus_values: Record<string, number>;
}

export interface BuildStats {
  damage_bonus: number;
  accuracy_bonus: number;
  defense_totals: Record<string, number>;
  resistance_totals: Record<string, number>;
  set_bonuses: string[];
}

// API service functions
export const gameDataApi = {
  // Health check
  async ping(): Promise<{ message: string }> {
    return apiClient.get<{ message: string }>("/ping");
  },

  // Archetype endpoints
  async getArchetypes(): Promise<Archetype[]> {
    return apiClient.get<Archetype[]>("/api/archetypes");
  },

  async getArchetype(id: number): Promise<Archetype> {
    return apiClient.get<Archetype>(`/api/archetypes/${id}`);
  },

  // Powerset endpoints
  async getPowerset(id: number): Promise<Powerset> {
    return apiClient.get<Powerset>(`/api/powersets/${id}`);
  },

  async getArchetypePowersets(archetypeId: number): Promise<Powerset[]> {
    return apiClient.get<Powerset[]>(
      `/api/archetypes/${archetypeId}/powersets`
    );
  },

  // Power endpoints
  async getPower(id: number): Promise<Power> {
    return apiClient.get<Power>(`/api/powers/${id}`);
  },

  // Enhancement endpoints
  async getEnhancements(): Promise<Enhancement[]> {
    return apiClient.get<Enhancement[]>("/api/enhancements");
  },

  async getValidEnhancements(powerId: number): Promise<Enhancement[]> {
    return apiClient.get<Enhancement[]>(`/api/enhancements?powerId=${powerId}`);
  },

  // Build calculation
  async calculateBuild(buildData: any): Promise<BuildStats> {
    return apiClient.post<BuildStats>("/api/calculate", buildData);
  },

  // Build import/export
  async encodeBuild(buildData: any): Promise<{ code: string }> {
    return apiClient.post<{ code: string }>("/api/build/encode", buildData);
  },

  async decodeBuild(code: string): Promise<any> {
    return apiClient.post<any>("/api/build/decode", { code });
  },
};

export default gameDataApi;
