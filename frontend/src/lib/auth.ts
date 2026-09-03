/** Auth utilities for frontend. */
import { api } from "./api/client";
import { User } from "@/types/api";

let userCache: User | null = null;

export async function getCurrentUser(): Promise<User | null> {
  if (userCache) return userCache;

  try {
    const user = await api.get<User>("/auth/me");
    userCache = user;
    return user;
  } catch {
    userCache = null;
    return null;
  }
}

export function clearUserCache() {
  userCache = null;
}

export function isAuthenticated(): boolean {
  return typeof window !== "undefined" && !!localStorage.getItem("access_token");
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function setToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function logout() {
  localStorage.removeItem("access_token");
  clearUserCache();
}