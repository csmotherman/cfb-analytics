-- Run once in the Supabase SQL editor used by Michigan Football Focus.
-- The public browser never talks directly to this table; /api/polls uses the service-role key.

create table if not exists public.poll_votes (
  poll_id text not null,
  device_hash text not null,
  option_id text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (poll_id, device_hash),
  constraint poll_votes_device_hash_length check (char_length(device_hash)=64)
);

create index if not exists poll_votes_poll_option_idx on public.poll_votes (poll_id, option_id);

alter table public.poll_votes enable row level security;
revoke all on public.poll_votes from anon, authenticated;
grant select, insert, update on public.poll_votes to service_role;

create or replace view public.poll_vote_totals as
select poll_id, option_id, count(*)::bigint as votes
from public.poll_votes
group by poll_id, option_id;

revoke all on public.poll_vote_totals from anon, authenticated;
grant select on public.poll_vote_totals to service_role;
