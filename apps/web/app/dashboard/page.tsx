import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "../../lib/supabase-server";
import Dashboard from "../../components/dashboard";

export default async function DashboardPage() {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");
  return <Dashboard userEmail={user.email ?? "adventurer"} />;
}
