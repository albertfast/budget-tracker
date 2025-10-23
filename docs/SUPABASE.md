# Supabase Integration (Auth + Profiles)

This document sets up Supabase Auth for the Expo app and creates a `profiles` table with RLS policies.

## 1) Create schema in Supabase

In the Supabase SQL editor, run `docs/SUPABASE.sql` from this repo.

This creates:
- `public.profiles` (1:1 with `auth.users`)
- RLS policies (self-access only)
- Trigger to auto-insert a profile row on signup

## 2) Configure Expo app with Supabase keys

Edit `mobile/app.json` and set:

```json
{
  "expo": {
    "scheme": "smartbudget",
    "extra": {
      "SUPABASE_URL": "https://YOUR-PROJECT-REF.supabase.co",
      "SUPABASE_ANON_KEY": "YOUR_SUPABASE_ANON_KEY"
    }
  }
}
```

## 3) Install dependencies (in `mobile/`)

```bash
npm i @supabase/supabase-js expo-auth-session react-native-url-polyfill react-native-get-random-values
```

No native config needed for these packages in managed Expo.

## 4) Client code

- `src/services/supabaseClient.ts` creates the client with persistent sessions.
- `src/services/supabaseAuth.ts` provides helpers:
  - `signInWithEmail(email, password)`
  - `signUpWithEmail(email, password)`
  - `signInWithGoogle()` (uses OAuth + AuthSession + PKCE)

`AccountScreen.tsx` is wired to these helpers (login, signup, Google sign-in buttons).

## 5) Deep linking for OAuth

- `app.json` includes `"scheme": "smartbudget"`.
- Google OAuth uses `makeRedirectUri({ scheme: 'smartbudget' })`.
- After OAuth, we call `supabase.auth.exchangeCodeForSession(url)` to finalize the session.

## 6) Optional: Use Supabase JWT with backend

If you want the FastAPI backend to accept Supabase JWTs, validate them with Supabase JWKS or via the `gotrue` issuer for your project. Otherwise, keep backend auth separate for now.

## 7) Test

- Email/Password: create a user in the Account screen and confirm email.
- Google: press "Continue with Google" and finish flow; you should return to the app logged in.
