-- Creator Hub schema. Run once against the provisioned Postgres database
-- (Vercel dashboard query editor, or `psql "$POSTGRES_URL" -f schema.sql`).
-- No migration framework -- this file is the whole schema; re-run safely
-- thanks to IF NOT EXISTS everywhere.

create table if not exists creators (
  id serial primary key,
  slug text not null unique,
  name text not null,
  pin_hash text not null,
  pin_salt text not null,
  created_at timestamptz not null default now()
);

create table if not exists creator_sessions (
  token text primary key,
  creator_id integer not null references creators(id) on delete cascade,
  expires_at timestamptz not null,
  created_at timestamptz not null default now()
);
create index if not exists creator_sessions_creator_id_idx on creator_sessions(creator_id);

create table if not exists creator_videos (
  id serial primary key,
  creator_id integer not null references creators(id) on delete cascade,
  slug text not null,
  title text not null,
  thesis text not null default '',
  hook text not null default '',
  status text not null default 'idea'
    check (status in ('idea','draft','researching','ready','recorded','published','archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (creator_id, slug)
);
create index if not exists creator_videos_creator_id_idx on creator_videos(creator_id);

create table if not exists creator_video_sections (
  id serial primary key,
  video_id integer not null references creator_videos(id) on delete cascade,
  title text not null,
  position integer not null default 0,
  talking_points text not null default '',
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists creator_video_sections_video_id_idx on creator_video_sections(video_id);

create table if not exists creator_research (
  id serial primary key,
  creator_id integer not null references creators(id) on delete cascade,
  title text not null,
  summary text not null default '',
  source_url text not null default '',
  body text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists creator_research_creator_id_idx on creator_research(creator_id);

create table if not exists creator_visuals (
  id serial primary key,
  creator_id integer not null references creators(id) on delete cascade,
  title text not null,
  image_url text not null default '',
  takeaway text not null default '',
  why_it_matters text not null default '',
  suggested_talking_point text not null default '',
  source text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists creator_visuals_creator_id_idx on creator_visuals(creator_id);

create table if not exists creator_requests (
  id serial primary key,
  creator_id integer not null references creators(id) on delete cascade,
  video_id integer not null references creator_videos(id) on delete cascade,
  section_id integer references creator_video_sections(id) on delete set null,
  request_type text not null default 'analytics'
    check (request_type in ('analytics','chart','research','fact_check')),
  what_you_need text not null,
  what_proving text not null default '',
  status text not null default 'open' check (status in ('open','in_progress','completed')),
  created_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists creator_requests_creator_id_idx on creator_requests(creator_id);
create index if not exists creator_requests_video_id_idx on creator_requests(video_id);

-- "author" is a plain label, not a second auth identity: this is a small,
-- trusted, two-person tool (creator + Carter), and Carter can already open
-- any workspace since he sets every PIN via the seed script. A dropdown at
-- note-creation time is enough to say who a note is from.
create table if not exists creator_notes (
  id serial primary key,
  creator_id integer not null references creators(id) on delete cascade,
  author text not null default 'creator' check (author in ('creator','carter')),
  body text not null,
  converted_video_id integer references creator_videos(id) on delete set null,
  -- Numeric CFBD gameId, not a foreign key: games live in the published
  -- game-stories.json artifact (Python-owned), not a Postgres table. Lets a
  -- quick note attach to a game without requiring a video yet.
  game_id integer,
  created_at timestamptz not null default now()
);
create index if not exists creator_notes_creator_id_idx on creator_notes(creator_id);
alter table creator_notes add column if not exists game_id integer;

-- Junction table: attaches reusable research/visuals/stories to a video
-- (section_id null = whole-video) or one specific section, without
-- duplicating the underlying content. A 'story' attachment isn't a Postgres
-- row -- game_id + story_id point into the published game-stories.json
-- artifact, the same way research_id/visual_id point at Postgres rows.
create table if not exists creator_attachments (
  id serial primary key,
  video_id integer not null references creator_videos(id) on delete cascade,
  section_id integer references creator_video_sections(id) on delete cascade,
  kind text not null,
  research_id integer references creator_research(id) on delete cascade,
  visual_id integer references creator_visuals(id) on delete cascade,
  game_id integer,
  story_id text,
  created_at timestamptz not null default now()
);
create index if not exists creator_attachments_video_id_idx on creator_attachments(video_id);
create index if not exists creator_attachments_section_id_idx on creator_attachments(section_id);
alter table creator_attachments add column if not exists game_id integer;
alter table creator_attachments add column if not exists story_id text;

-- Idempotent constraint (re)installation: drop whatever check constraints
-- already exist on this table (auto-generated names vary by how the table
-- was first created) and install the current 3-branch shape fresh, so this
-- file stays safe to re-run against a database created before 'story'
-- attachments existed.
do $$
declare
  constraint_name text;
begin
  for constraint_name in
    select conname from pg_constraint
    where conrelid = 'creator_attachments'::regclass and contype = 'c'
  loop
    execute format('alter table creator_attachments drop constraint %I', constraint_name);
  end loop;
end $$;
alter table creator_attachments add constraint creator_attachments_kind_check
  check (kind in ('research', 'visual', 'story'));
alter table creator_attachments add constraint creator_attachments_shape_check
  check (
    (kind = 'research' and research_id is not null and visual_id is null and game_id is null and story_id is null) or
    (kind = 'visual' and visual_id is not null and research_id is null and game_id is null and story_id is null) or
    (kind = 'story' and game_id is not null and story_id is not null and research_id is null and visual_id is null)
  );
