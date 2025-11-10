import { api } from "./api";

export const evaluatePassword = async (password: string) => {
  try {
    const response = await api.post("/evaluate", { password });
    return response.data;
  } catch (error: any) {
    console.error("Error evaluating password:", error);
    return { error: "Failed to reach backend" };
  }
};

export const generatePassword = async (base: string) => {
  try {
    const response = await api.post("/generate_password", { base });
    return response.data;
  } catch (error: any) {
    console.error("Error generating password:", error);
    return { error: "Failed to generate password" };
  }
};
