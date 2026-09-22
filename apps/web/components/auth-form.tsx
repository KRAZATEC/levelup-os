"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { createClient } from "../lib/supabase";

export default function AuthForm() {
  const supabase = createClient();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setMessage("");
    const result = mode === "login"
      ? await supabase.auth.signInWithPassword({ email, password })
      : await supabase.auth.signUp({ email, password, options: { emailRedirectTo: `${window.location.origin}/auth/callback` } });
    if (result.error) setMessage(result.error.message);
    else if (mode === "signup") setMessage("Check your email to confirm your account.");
    else window.location.href = "/dashboard";
    setLoading(false);
  }

  return <section className="auth-card"><Link className="brand" href="/">LEVELUPOS</Link><div className="eyebrow" style={{ marginTop: 60 }}>{mode === "login" ? "Welcome back" : "Create your account"}</div><h1>{mode === "login" ? "Resume your adventure." : "Start your adventure."}</h1><p className="muted">Your quests and progress are waiting.</p><form onSubmit={submit} className="auth-form"><input className="input" type="email" placeholder="Email address" value={email} onChange={(event) => setEmail(event.target.value)} required /><input className="input" type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={6} required /><button className="button" disabled={loading}>{loading ? "Loading..." : mode === "login" ? "Log in" : "Create account"}</button></form>{message && <p className="error">{message}</p>}<button className="text-button" onClick={() => setMode(mode === "login" ? "signup" : "login")}>{mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}</button></section>;
}
