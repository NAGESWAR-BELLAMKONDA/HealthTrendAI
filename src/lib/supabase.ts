import { createClient } from '@supabase/supabase-js';
// This is a public publishable key; table access is protected by Supabase RLS.
// Never replace it with a service-role or secret key in browser code.
const url=(import.meta.env.VITE_SUPABASE_URL as string|undefined) ?? 'https://ugitalbazfmeqwuscizq.supabase.co';
const key=(import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string|undefined) ?? 'sb_publishable_CMjOtCoYxlnUg3oDHQI8HQ_Uc1g6_GO';
export const supabase=createClient(url,key);
export const isSupabaseConfigured=true;