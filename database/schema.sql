-- Database Schema for Motivational Message App
-- PostgreSQL

-- User messages table
CREATE TABLE IF NOT EXISTS user_messages (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    message VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    feedback VARCHAR(500) NOT NULL,
    rating INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_messages_username ON user_messages(username);
CREATE INDEX IF NOT EXISTS idx_user_messages_created_at ON user_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_user_feedback_username ON user_feedback(username);
CREATE INDEX IF NOT EXISTS idx_user_feedback_rating ON user_feedback(rating);

-- Sample data
INSERT INTO user_messages (username, message) VALUES
('Alice', 'you can make it 💪'),
('Bob', 'great things are coming your way 🌟'),
('Charlie', 'keep pushing forward 🚀'),
('Diana', 'you are stronger than you think 🔥'),
('Eve', 'success is within your reach 🎯')
ON CONFLICT DO NOTHING;

-- View to get message statistics
CREATE OR REPLACE VIEW message_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_messages,
    COUNT(DISTINCT username) as unique_users
FROM user_messages
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Query to get most active users
-- SELECT username, COUNT(*) as message_count 
-- FROM user_messages 
-- GROUP BY username 
-- ORDER BY message_count DESC 
-- LIMIT 10;