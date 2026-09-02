-- ============================================================
--  オニWorks Supabase スキーマ
--  Supabase の SQL Editor に貼り付けて実行してください。
-- ============================================================

create table if not exists movies (
  id          text primary key,
  title       text not null,
  release_date date,
  status      text,            -- 'now' | 'upcoming'
  genre       text[],
  overview    text,
  poster      text,
  popularity  numeric,
  source      text,
  updated_at  timestamptz default now()
);

create table if not exists kinro (
  id        text primary key,
  air_date  date,
  title     text not null,
  note      text,
  source    text,
  updated_at timestamptz default now()
);

create table if not exists games (
  id          text primary key,
  title       text not null,
  release_date date,
  platforms   text[],
  genre       text[],
  image       text,
  popularity  numeric,
  source      text,
  updated_at  timestamptz default now()
);

create table if not exists topics (
  id          text primary key,
  category    text not null,   -- 'minecraft' | 'roblox' | 'meme'
  name        text not null,
  type        text,
  url         text,
  metric      text,
  updated     date,
  description text,
  source      text,
  updated_at  timestamptz default now()
);

create table if not exists ideas (
  id         text primary key,
  title      text not null,
  hook       text,
  body       text,
  based_on   text[],
  tags       text[],
  score      int,
  updated_at timestamptz default now()
);

-- ------------------------------------------------------------
--  RLS: 誰でも「閲覧」だけ許可（anonキーで読み取り可）。
--  書き込みは service_role キー(GitHub Actions)のみ。
-- ------------------------------------------------------------
alter table movies enable row level security;
alter table kinro  enable row level security;
alter table games  enable row level security;
alter table topics enable row level security;
alter table ideas  enable row level security;

do $$
declare t text;
begin
  foreach t in array array['movies','kinro','games','topics','ideas'] loop
    execute format('drop policy if exists "public read %1$s" on %1$s;', t);
    execute format('create policy "public read %1$s" on %1$s for select using (true);', t);
  end loop;
end $$;
-- service_role キーは RLS を自動的にバイパスするため、書き込みポリシーは不要です。
