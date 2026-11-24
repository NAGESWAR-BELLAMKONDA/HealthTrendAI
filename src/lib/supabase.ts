import { createClient } from '@supabase/supabase-js';

// Public browser credentials only. Never place the service-role key in Vite.
const url = (import.meta.env.VITE_SUPABASE_URL as string | undefined) ?? 'https://ugitalbazfmeqwuscizq.supabase.co';
const key = (import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined) ?? 'sb_publishable_CMjOtCoYxlnUg3oDHQI8HQ_Uc1g6_GO';

export const isSupabaseConfigured = Boolean(url && key);
export const supabase = createClient(url, key, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
});
