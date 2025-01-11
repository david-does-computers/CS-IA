DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS study_session;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS task_tag;
DROP TABLE IF EXISTS study_session_tasks;



-- Users Table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL CHECK(length(username) <= 15),
    password TEXT NOT NULL CHECK(length(password) >= 8)
);

-- Tasks Table
CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    priority INTEGER CHECK (priority BETWEEN 1 AND 10),
    due_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category(category_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK(length(name) <= 20),
    FOREIGN KEY (user_id) REFERENCES user(id),
    UNIQUE (user_id, name)
);