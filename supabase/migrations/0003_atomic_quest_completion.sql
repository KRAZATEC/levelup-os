create or replace function public.complete_quest_atomic(
  p_quest_id uuid,
  p_user_id uuid
)
returns table (
  quest jsonb,
  xp_awarded integer,
  total_xp integer,
  level integer
)
language plpgsql
security invoker
set search_path = public
as $$
declare
  v_quest public.quests%rowtype;
  v_profile public.profiles%rowtype;
  v_xp integer;
  v_total_xp integer;
  v_level integer;
  v_skill record;
begin
  select * into v_quest
  from public.quests
  where id = p_quest_id and user_id = p_user_id
  for update;

  if not found then
    raise exception 'Quest not found';
  end if;

  if v_quest.status = 'completed' then
    raise exception 'Quest already completed';
  end if;

  v_xp := 20 + (v_quest.difficulty * 15) + (least(coalesce(v_quest.estimated_minutes, 0) / 30, 4) * 5);

  update public.quests
  set status = 'completed', completed_at = now(), updated_at = now()
  where id = p_quest_id
  returning * into v_quest;

  select * into v_profile
  from public.profiles
  where id = p_user_id
  for update;

  if not found then
    raise exception 'Profile not found';
  end if;

  v_total_xp := v_profile.total_xp + v_xp;
  v_level := greatest(1, floor(power(v_total_xp::numeric / 100, 1 / 1.5))::integer + 1);

  update public.profiles
  set total_xp = v_total_xp, level = v_level, updated_at = now()
  where id = p_user_id;

  insert into public.xp_transactions (user_id, quest_id, amount, reason)
  values (p_user_id, p_quest_id, v_xp, 'Completed quest: ' || v_quest.title);

  for v_skill in
    select qs.skill_id, qs.xp_reward
    from public.quest_skills qs
    where qs.quest_id = p_quest_id
  loop
    insert into public.user_skills (user_id, skill_id, level, xp)
    values (p_user_id, v_skill.skill_id, 1, v_skill.xp_reward)
    on conflict (user_id, skill_id) do update
      set xp = public.user_skills.xp + excluded.xp,
          level = greatest(1, floor(power((public.user_skills.xp + excluded.xp)::numeric / 100, 1 / 1.5))::integer + 1),
          updated_at = now();

    insert into public.xp_transactions (user_id, quest_id, skill_id, amount, reason)
    values (p_user_id, p_quest_id, v_skill.skill_id, v_skill.xp_reward, 'Skill progress: ' || v_quest.title);
  end loop;

  return query select to_jsonb(v_quest), v_xp, v_total_xp, v_level;
end;
$$;

revoke execute on function public.complete_quest_atomic(uuid, uuid) from anon;
grant execute on function public.complete_quest_atomic(uuid, uuid) to authenticated;
