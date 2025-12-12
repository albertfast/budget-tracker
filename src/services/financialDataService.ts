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

async function getOrCreateManualBankAccount(userId: string): Promise<string> {
  // Check if user has a manual bank account
  const { data: accounts, error: fetchError } = await supabase
    .from('bank_accounts')
    .select('id')
    .eq('user_id', userId)
    .eq('account_name', 'Manual Entry')
    .eq('account_type', 'cash')
    .limit(1);

  if (fetchError) throw fetchError;

  if (accounts && accounts.length > 0) {
    return accounts[0].id;
  }

  // Create manual bank account
  const { data: newAccount, error: insertError } = await supabase
    .from('bank_accounts')
    .insert({
      user_id: userId,
      account_name: 'Manual Entry',
      bank_name: 'Manual',
      account_type: 'cash',
      is_active: true,
    })
    .select('id')
    .single();

  if (insertError) throw insertError;
  return newAccount.id;
}

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
  // User-scoped insert that respects RLS on transactions
  const { data: userResult, error: userError } = await supabase.auth.getUser();
  if (userError) throw userError;
  const user = userResult.user;
  if (!user) throw new Error('User must be signed in to add records');

  // Get or create manual bank account
  const bankAccountId = await getOrCreateManualBankAccount(user.id);

  // Map to transactions table schema
  const { error } = await supabase.from('transactions').insert({
    bank_account_id: bankAccountId,
    amount: record.amount,
    description: record.memo || record.merchant || '',
    category_primary: record.category,
    category_detailed: record.category,
    date: record.occurred_on,
    is_manual: true,
    is_pending: false,
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
