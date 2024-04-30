CREATE TABLE users (
    user_id INTEGER PRIMARY KEY NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE scorecard (
    scorecard_id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    points INTEGER CHECK(points IN (0,1)),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE verbs (
    verb_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT('custom'),
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE temp_table(name TEXT NOT NULL);
.import static/irregular.csv temp_table
INSERT INTO verbs(name) SELECT * FROM temp_table;
UPDATE verbs SET type = 'irregular';
DROP TABLE temp_table;

CREATE TABLE temp_table(name TEXT NOT NULL);
.import static/regular.csv temp_table
INSERT INTO verbs(name) SELECT * FROM temp_table;
UPDATE verbs SET type = 'regular' WHERE type = 'custom';
DROP TABLE temp_table;

CREATE TABLE moods (
    mood_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE tenses (
    tense_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE
);
