export type Quest = {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  quest_type: "main" | "side" | "daily" | "challenge";
  status: "pending" | "in_progress" | "completed" | "skipped" | "archived";
  category?: string | null;
  priority: "low" | "medium" | "high" | "urgent";
  difficulty: number;
  estimated_minutes?: number | null;
  scheduled_date?: string | null;
  deadline?: string | null;
  completed_at?: string | null;
  source: string;
  created_at: string;
  updated_at: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(token: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(init?.headers ?? {}) } });
  if (!response.ok) throw new Error(await response.text());
  if (response.status === 204) return undefined as T;
  return response.json();
}

export function listQuests(token: string) { return request<Quest[]>(token, "/api/v1/quests"); }
export function createQuest(token: string, payload: Partial<Quest>) { return request<Quest>(token, "/api/v1/quests", { method: "POST", body: JSON.stringify(payload) }); }
export function completeQuest(token: string, id: string) { return request<{ quest: Quest; xp_awarded: number; level: number; total_xp: number }>(token, `/api/v1/quests/${id}/complete`, { method: "POST" }); }
