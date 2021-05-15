CREATE TABLE netflix(
   "show_id" TEXT PRIMARY KEY     NOT NULL,
   "type"           TEXT    NOT NULL,
   "title"            TEXT     NOT NULL,
   "director"        TEXT,
   "cast"        TEXT,
   "country"        TEXT,
   "date_added"        TEXT,
   "release_year"        INT,
   "rating"        TEXT,
   "duration"        TEXT,
   "listed_in"        TEXT,
   "description"        TEXT
);