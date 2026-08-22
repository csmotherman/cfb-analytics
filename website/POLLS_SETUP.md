# Fan polls backend setup

The UI and `/api/polls` route are already implemented. Community percentages need one persistent Supabase table.

1. Create/use a Supabase project.
2. Run `supabase/fan-polls.sql` once in the Supabase SQL editor.
3. Add these Vercel environment variables to the website project:
   - `SUPABASE_URL` — Project URL.
   - `SUPABASE_SERVICE_ROLE_KEY` — server-only service-role key. Never expose it with a `NEXT_PUBLIC_` prefix.
   - `POLL_DEVICE_SALT` — optional extra secret used when hashing the browser/device ID. If omitted, the service-role key is used as the salt.
4. Redeploy once after the environment variables are saved.

## Voting behavior

- The browser creates a random ID and stores it in localStorage.
- The server hashes that ID before persistence; raw device IDs are never stored.
- `(poll_id, device_hash)` is the primary key, so a browser/device profile can only have one active vote per poll.
- Picking a different answer updates the existing row instead of creating a second vote.
- Community percentages are computed from the aggregate `poll_vote_totals` view.
- Results refresh on page load, immediately after a vote, and once per minute while the page is visible.

This is intentionally account-free. Clearing browser storage or using another browser profile creates a new device identity, so this is a practical fan-poll guard rather than fraud-proof identity verification.
