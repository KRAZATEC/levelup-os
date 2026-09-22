import Link from "next/link";

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar"><div className="brand">LEVELUPOS</div><Link className="button" href="/dashboard">Open dashboard</Link></header>
      <section className="content" style={{ maxWidth: 980, margin: "0 auto", paddingTop: 110 }}>
        <div className="eyebrow">Life RPG · QuestFlow · Skill Tree</div>
        <h1 style={{ fontSize: "clamp(42px, 8vw, 84px)", maxWidth: 850 }}>Turn your real life into a game worth playing.</h1>
        <p className="muted" style={{ fontSize: 19, lineHeight: 1.7, maxWidth: 680, marginTop: 22 }}>Capture goals, complete quests, earn XP, and build skills that reflect who you are becoming.</p>
        <Link className="button" style={{ display: "inline-block", marginTop: 24, textDecoration: "none" }} href="/dashboard">Start your adventure →</Link>
      </section>
    </main>
  );
}
