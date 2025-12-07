import { supabase } from './supabaseClient';

type UpsertProfileInput = {
  username?: string;
  full_name?: string;
  avatar_url?: string;
  default_currency?: string;
};

export type FinancialRecordInput = {
  category: string;
  amount: number;
  currency: string;
  occurred_on: string; // ISO date string
  merchant?: string;
  memo?: string;
  source?: 'plaid' | 'manual' | 'import';
};

export async function upsertProfile(update: UpsertProfileInput) {
  // Make sure we only write profile rows for the signed-in user
  const { data: userResult, error: userError } = await supabase.auth.getUser();
  if (userError) throw userError;
  const user = userResult.user;
  if (!user) throw new Error('User must be signed in to update profile');

  const payload = {
    id: user.id,
    email: user.email,
    ...update,
    updated_at: new Date().toISOString(),
  };

  const { error } = await supabase.from('profiles').upsert(payload, { onConflict: 'id' });
  if (error) throw error;
  return payload;
}

export async function insertFinancialRecord(record: FinancialRecordInput) {
  // User-scoped insert that respects RLS on financial_records
  const { data: userResult, error: userError } = await supabase.auth.getUser();
  if (userError) throw userError;
  const user = userResult.user;
  if (!user) throw new Error('User must be signed in to add records');

  const { error } = await supabase.from('financial_records').insert({
    user_id: user.id,
    ...record,
  });
  if (error) throw error;
}

export async function uploadBankStatement(opts: {
  fileUri: string;
  filename: string;
  contentType?: string;
}) {
  // Uploads to user-specific folder; bucket RLS blocks cross-user access
  const { fileUri, filename, contentType = 'application/pdf' } = opts;
  const { data: userResult, error: userError } = await supabase.auth.getUser();
  if (userError) throw userError;
  const user = userResult.user;
  if (!user) throw new Error('User must be signed in to upload statements');

  const path = `${user.id}/${Date.now()}-${filename.replace(/\s+/g, '-')}`;
  const response = await fetch(fileUri);
  const blob = await response.blob();

  const { error } = await supabase.storage
    .from('bank-statements')
    .upload(path, blob, { contentType, upsert: false });
  if (error) throw error;

  const { data: signedUrl, error: signedError } = await supabase.storage
    .from('bank-statements')
    .createSignedUrl(path, 60 * 60 * 12);
  if (signedError) throw signedError;

  return { path, signedUrl: signedUrl?.signedUrl };
}
