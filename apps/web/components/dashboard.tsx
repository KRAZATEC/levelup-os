"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { createQuest, listQuests, completeQuest, type Quest } from "../lib/api";
import { createClient } from "../lib/supabase";

export default function Dashboard({ userEmail }: { userEmail: string }) {
  const supabase = createClient();
  const [quests, setQuests] = useState<Quest[]>([]);
  const [title, setTitle] = useState("");
  const [difficulty, setDifficulty] = useState("2");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalXp, setTotalXp] = useState(0);
  const [profileLevel, setProfileLevel] = useState(1);

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data }) => {
      const token = data.session?.access_token;
      if (!token) return;
      try { const [loaded, profile] = await Promise.all([listQuests(token), fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/profiles?id=eq.${data.session?.user.id}&select=total_xp,level`, { headers: { apikey: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!, Authorization: `Bearer ${token}` } }).then((response) => response.json())]); setQuests(loaded); if (profile[0]) { setTotalXp(profile[0].total_xp); setProfileLevel(profile[0].level); } } catch { setError("Could not load your progress."); }
    });
  }, []);

  const level = profileLevel;
  const levelNext = Math.floor(100 * Math.pow(level, 1.5));
  const levelBase = Math.floor(100 * Math.pow(Math.max(0, level - 1), 1.5));
  const levelProgress = Math.min(100, Math.max(0, ((totalXp - levelBase) / Math.max(1, levelNext - levelBase)) * 100));
  const completed = useMemo(() => quests.filter((quest) => quest.status === "completed").length, [quests]);

  async function token() { return (await supabase.auth.getSession()).data.session?.access_token ?? ""; }
  async function handleCreate(event: FormEvent) { event.preventDefault(); if (!title.trim()) return; setLoading(true); setError(""); try { const quest = await createQuest(await token(), { title: title.trim(), difficulty: Number(difficulty), estimated_minutes: 30, priority: "medium", quest_type: "side", source: "manual" }); setQuests((current) => [quest, ...current]); setTitle(""); } catch { setError("Could not create quest."); } finally { setLoading(false); } }
  async function handleComplete(quest: Quest) { try { const result = await completeQuest(await token(), quest.id); setQuests((current) => current.map((item) => item.id === quest.id ? result.quest : item)); setTotalXp(result.total_xp); setProfileLevel(result.level); } catch { setError("Could not complete quest."); } }
  async function logout() { await supabase.auth.signOut(); window.location.href = "/login"; }

  return <main className="shell"><header className="topbar"><div className="brand">LEVELUPOS</div><div className="topbar-meta"><span>{userEmail}</span><button className="button secondary" onClick={logout}>Log out</button></div></header><div className="layout"><aside className="sidebar"><a className="nav-item active" href="/dashboard">Dashboard</a><a className="nav-item" href="#quests">Quests</a><a className="nav-item" href="#skills">Skill tree</a><a className="nav-item" href="#focus">Focus mode</a></aside><section className="content"><div className="heading-row"><div><div className="eyebrow">Your command center</div><h1>Good evening, builder.</h1><p className="muted">Make today count, one quest at a time.</p></div><button className="button secondary" onClick={() => setError("AI QuestFlow is coming in the next phase.")}>✦ AI QuestFlow</button></div><div className="grid stats"><div className="card"><div className="stat-label">Current level</div><div className="stat-value">{level}</div><div className="muted">XP adventurer</div></div><div className="card"><div className="stat-label">Total XP</div><div className="stat-value">{totalXp}</div><div className="muted">Keep climbing</div></div><div className="card"><div className="stat-label">Completed quests</div><div className="stat-value">{completed}</div><div className="muted">This session</div></div><div className="card"><div className="stat-label">Streak</div><div className="stat-value">0 days</div><div className="muted">Start your streak</div></div></div><div className="grid main-grid"><section className="card" id="quests"><div className="eyebrow">Today's missions</div><h2>Quest board</h2><form className="quest-form" onSubmit={handleCreate}><input className="input" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="What do you want to accomplish?" /><div style={{ display: "flex", gap: 8 }}><select className="select" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}><option value="1">Easy</option><option value="2">Medium</option><option value="3">Hard</option><option value="4">Epic</option><option value="5">Boss</option></select><button className="button" disabled={loading}>{loading ? "..." : "Add quest"}</button></div></form>{error && <div className="error">{error}</div>}<div style={{ marginTop: 16 }}>{quests.length === 0 ? <div className="empty">No quests yet. Add your first mission above.</div> : quests.map((quest) => <div className="quest" key={quest.id}><div><div className="quest-title">{quest.title}</div><div className="quest-meta"><span className={`badge ${quest.quest_type}`}>{quest.quest_type}</span> · Difficulty {quest.difficulty} · {quest.status}</div></div><div className="quest-actions">{quest.status !== "completed" && <button className="button" onClick={() => handleComplete(quest)}>Complete</button>}{quest.status === "completed" && <span className="badge main">Completed ✓</span>}</div></div>)}</div></section><aside className="card" id="skills"><div className="eyebrow">Progression</div><h2>Skill tree</h2><p className="muted">Your real-world stats are built through action.</p>{["Backend Engineering", "AI / ML", "DSA", "Cloud & DevOps"].map((name, index) => <div className="skill-row" key={name}><div className="skill-head"><span>{name}</span><span>{[72, 58, 46, 34][index]}%</span></div><div className="progress-track"><div className="progress-fill" style={{ width: `${[72, 58, 46, 34][index]}%` }} /></div></div>)}<div className="card" style={{ marginTop: 24, background: "#0d0d10" }}><div className="stat-label">Level progress</div><div className="stat-value" style={{ fontSize: 22 }}>{totalXp} / {levelNext} XP</div><div className="progress-track"><div className="progress-fill" style={{ width: `${levelProgress}%` }} /></div></div></aside></div></section></div></main>;
}
