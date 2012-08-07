DROP TABLE IF EXISTS jobs, builds, buildservers;

CREATE TABLE jobs (
  id serial primary key,
  commit_hash text,
  builder text 
);

CREATE TABLE builds (
  id serial primary key,
  job_id int references jobs,
  log text
);

CREATE TABLE buildservers (
  id serial primary key,
  git_url text,
  short_name text,
  currently_building int references builds
);
