DROP TABLE IF EXISTS jobs, builds, buildservers;

CREATE TABLE jobs (
  id serial primary key,
  commit_hash text,
  builder text,
  done boolean default 'f',
  created_at timestamp default now,
  message text,
  author text,
  success boolean
);

CREATE TABLE builds (
  id serial primary key,
  job_id int references jobs,
  log text default '',
  updated_at timestamp,
  done boolean default 'f',
  success boolean
);

CREATE TABLE buildservers (
  id serial primary key,
  git_url text,
  short_name text,
  building int references builds
);
