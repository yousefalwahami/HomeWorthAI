CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE chat_logs (
    chat_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    chat_title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    chat_id INT REFERENCES chat_logs(chat_id),
    sender VARCHAR(100) NOT NULL,
    receiver VARCHAR(100),
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE images (
    image_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    filename VARCHAR(255) NOT NULL,
    items TEXT, 
    image_data BYTEA NOT NULL, 
    uploaded_at TIMESTAMP DEFAULT NOW()
);
