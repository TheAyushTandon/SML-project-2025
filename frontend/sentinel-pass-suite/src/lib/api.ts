// src/lib/api.ts
import axios from "axios";

// Base URL for FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// -----------------------------
// 🔹 Type Definitions
// -----------------------------

export interface PasswordEvaluation {
  strength: string;
  classifier_probabilities: {
    weak: number;
    medium: number;
    strong: number;
  };
  leak_risk: {
    score: number;
    is_leaked: boolean;
    message: string;
  };
  anomaly_detection: {
    score: number;
    is_anomaly: boolean;
    reconstruction_error: number;
  };
  feedback: string[];
}

export interface GeneratePasswordRequest {
  base: string;
}

export interface GeneratePasswordResponse {
  status: string;
  base: string;
  best_password: string;
  suggestions: string[];
}

// -----------------------------
// 🔹 API Client
// -----------------------------
export const api = {
  /**
   * Evaluate password using Model A + B + C ensemble
   */
  evaluatePassword: async (password: string): Promise<PasswordEvaluation> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/evaluate`, { password }, {
        headers: { "Content-Type": "application/json" },
      });

      // Return backend response directly (it already matches the expected format)
      return response.data;
    } catch (error: any) {
      console.error("Error evaluating password:", error);
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || "Failed to evaluate password");
      }
      throw error;
    }
  },

  /**
   * Generate a password based on base word
   */
  generatePassword: async (params: GeneratePasswordRequest): Promise<GeneratePasswordResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/generate_password`, params, {
        headers: { "Content-Type": "application/json" },
      });

      return response.data;
    } catch (error: any) {
      console.error("Error generating password:", error);
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || "Failed to generate password");
      }
      throw error;
    }
  },
};
