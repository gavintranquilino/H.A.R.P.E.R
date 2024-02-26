CREATE TABLE IF NOT EXISTS prefixes (
  id integer PRIMARY KEY,
  prefix text
);

CREATE TABLE IF NOT EXISTS homework (
  id integer PRIMARY KEY,
  fullname text,
  topic text
)