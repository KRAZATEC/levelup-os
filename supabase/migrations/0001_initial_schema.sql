create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique,
  display_name text,
  timezone text not null default 'Asia/Kolkata',
  level integer not null default 1 check (level >= 1),
  total_xp integer not null default 0 check (total_xp >= 0),
  coins integer not null default 0 check (coins >= 0),
  current_streak integer not null default 0 check (current_streak >= 0),
  longest_streak integer not null default 0 check (longest_streak >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.skills (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  description text,
  parent_skill_id uuid references public.skills(id) on delete set null,
  icon text,
  color text,
  created_at timestamptz not null default now()
);

create table if not exists public.user_skills (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  level integer not null default 1 check (level >= 1),
  xp integer not null default 0 check (xp >= 0),
  target_level integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, skill_id)
);

create table if not exists public.quests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text,
  quest_type text not null default 'side' check (quest_type in ('main', 'side', 'daily', 'challenge')),
  status text not null default 'pending' check (status in ('pending', 'in_progress', 'completed', 'skipped', 'archived')),
  category text,
  priority text not null default 'medium' check (priority in ('low', 'medium', 'high', 'urgent')),
  difficulty integer not null default 1 check (difficulty between 1 and 5),
  estimated_minutes integer check (estimated_minutes is null or estimated_minutes > 0),
  scheduled_date date,
  deadline timestamptz,
  completed_at timestamptz,
  source text not null default 'manual' check (source in ('manual', 'ai', 'voice', 'imported')),
  parent_quest_id uuid references public.quests(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.quest_skills (
  quest_id uuid not null references public.quests(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  xp_reward integer not null default 0 check (xp_reward >= 0),
  primary key (quest_id, skill_id)
);

create table if not exists public.xp_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  quest_id uuid references public.quests(id) on delete set null,
  skill_id uuid references public.skills(id) on delete set null,
  amount integer not null check (amount > 0),
  reason text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.focus_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  quest_id uuid references public.quests(id) on delete set null,
  planned_minutes integer not null check (planned_minutes > 0),
  actual_minutes integer,
  status text not null default 'planned' check (status in ('planned', 'active', 'completed', 'cancelled')),
  started_at timestamptz,
  ended_at timestamptz,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.daily_reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  review_date date not null,
  mood integer check (mood is null or mood between 1 and 5),
  energy integer check (energy is null or energy between 1 and 5),
  summary text,
  wins text[],
  blockers text[],
  ai_insight text,
  created_at timestamptz not null default now(),
  unique(user_id, review_date)
);

alter table public.profiles enable row level security;
alter table public.user_skills enable row level security;
alter table public.quests enable row level security;
alter table public.quest_skills enable row level security;
alter table public.xp_transactions enable row level security;
alter table public.focus_sessions enable row level security;
alter table public.daily_reviews enable row level security;

create policy "profiles_owner_select" on public.profiles for select using (auth.uid() = id);
create policy "profiles_owner_update" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);
create policy "user_skills_owner_all" on public.user_skills for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "quests_owner_all" on public.quests for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "quest_skills_owner_all" on public.quest_skills for all using (exists (select 1 from public.quests q where q.id = quest_id and q.user_id = auth.uid())) with check (exists (select 1 from public.quests q where q.id = quest_id and q.user_id = auth.uid()));
create policy "xp_owner_all" on public.xp_transactions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "focus_owner_all" on public.focus_sessions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "reviews_owner_all" on public.daily_reviews for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

insert into public.skills (slug, name, description, icon, color) values
  ('ai-ml', 'AI/ML', 'Machine learning and intelligent systems', 'brain', '#8b5cf6'),
  ('backend-engineering', 'Backend Engineering', 'APIs, services, and server-side systems', 'server', '#3b82f6'),
  ('full-stack', 'Full-Stack Development', 'Frontend and backend product development', 'layers', '#06b6d4'),
  ('cybersecurity', 'Cybersecurity', 'Security analysis and defensive engineering', 'shield', '#ef4444'),
  ('cloud-devops', 'Cloud and DevOps', 'Deployment, infrastructure, and reliability', 'cloud', '#f59e0b'),
  ('dsa', 'Data Structures and Algorithms', 'Problem solving and algorithmic thinking', 'code', '#10b981'),
  ('communication', 'Communication', 'Writing, speaking, and technical explanation', 'message', '#ec4899'),
  ('health', 'Health', 'Physical and mental wellbeing', 'heart', '#22c55e'),
  ('finance', 'Finance', 'Personal financial awareness and discipline', 'wallet', '#84cc16'),
  ('discipline', 'Discipline', 'Consistency and execution', 'target', '#64748b')
on conflict (slug) do nothing;

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'full_name', new.email));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();
