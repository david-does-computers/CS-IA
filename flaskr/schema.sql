DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS study_session;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS task_tag;
DROP TABLE IF EXISTS study_session_tasks;



-- Users Table
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Tasks Table
CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category TEXT CHECK(category IN ('assignment', 'test_revision', 'misc')) NOT NULL,
    priority INTEGER CHECK (priority BETWEEN 1 AND 10),
    due_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Tags Table
CREATE TABLE tag (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    UNIQUE(user_id, tag_name), -- Prevent duplicate tags for the same user
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- TaskTags Table (Many-to-Many Relationship)
CREATE TABLE task_tag (
    task_tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES task(task_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE
);

-- Study Sessions Table
CREATE TABLE study_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    total_time_minutes INTEGER NOT NULL,
    points_earned INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Study Session Tasks Table (many-to-many relationship)
CREATE TABLE study_session_tasks (
    session_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL DEFAULT 0,
    planned_minutes INTEGER NOT NULL,
    completed_minutes INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES StudySessions(session_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id)
);


-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL,
--   FOREIGN KEY (author_id) REFERENCES user (id)
-- );
