import type { AdminOverview, LessonResponse, PetFeedResponse, PetSummary, SessionCompleteResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Request failed: ${response.status} ${body}`);
  }
  return response.json() as Promise<T>;
}

export const apiClient = {
  health: () => request<{ status: string }>("/health"),
  nextLesson: (payload: unknown) => request<LessonResponse>("/lessons/next", { method: "POST", body: JSON.stringify(payload) }),
  completeSession: (payload: unknown) => request<SessionCompleteResponse>("/sessions/complete", { method: "POST", body: JSON.stringify(payload) }),
  getPet: (studentId: string) => request<PetSummary>(`/pets/${studentId}`),
  feedPet: (payload: unknown) => request<PetFeedResponse>("/pets/feed", { method: "POST", body: JSON.stringify(payload) }),
  adminOverview: () => request<AdminOverview>("/admin/overview"),
};
