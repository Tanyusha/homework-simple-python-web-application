drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  user text not null
);

create table users (
  id integer primary key autoincrement,
  user text UNIQUE,
  password text not null
);