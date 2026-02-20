-- ============================================
-- MySQL QUERIES FOR AI_SPEECH DATABASE
-- Copy and paste these into your MySQL application
-- ============================================

-- 1. CONNECT TO DATABASE
USE AI_Speech;

-- ============================================
-- VIEW ALL USERS
-- ============================================

-- View all users with basic info
SELECT * FROM users;

-- View users with formatted output
SELECT 
    user_id,
    name,
    email,
    role,
    is_active,
    email_verified,
    created_at,
    last_login
FROM users
ORDER BY created_at DESC;

-- ============================================
-- VIEW USER CREDENTIALS
-- ============================================

-- View user emails and roles (passwords are hashed)
SELECT 
    user_id,
    name,
    email,
    role,
    LEFT(password_hash, 30) AS password_preview,
    is_active
FROM users;

-- ============================================
-- VIEW USAGE LOGS
-- ============================================

-- View user usage information
SELECT 
    ul.usage_id,
    u.name,
    u.email,
    ul.total_uses,
    ul.remaining_uses,
    ul.last_used_at,
    ul.reset_date
FROM usage_logs ul
JOIN users u ON ul.user_id = u.user_id
ORDER BY ul.last_used_at DESC;

-- ============================================
-- VIEW SUBSCRIPTIONS
-- ============================================

-- View all subscriptions
SELECT * FROM subscriptions;

-- View active subscriptions with user info
SELECT 
    s.subscription_id,
    u.name,
    u.email,
    s.plan_type,
    s.start_date,
    s.end_date,
    s.is_active,
    s.amount,
    s.currency,
    s.payment_status
FROM subscriptions s
JOIN users u ON s.user_id = u.user_id
WHERE s.is_active = TRUE
ORDER BY s.start_date DESC;

-- ============================================
-- VIEW AUDIO PROCESSING HISTORY
-- ============================================

-- View recent audio processing history
SELECT 
    ah.audio_id,
    u.name AS user_name,
    u.email,
    ah.original_filename,
    ah.output_mode,
    ah.processing_duration,
    ah.file_size_mb,
    ah.created_at
FROM audio_history ah
JOIN users u ON ah.user_id = u.user_id
ORDER BY ah.created_at DESC
LIMIT 20;

-- View audio history for specific user
SELECT 
    audio_id,
    original_filename,
    output_mode,
    processing_duration,
    file_size_mb,
    created_at
FROM audio_history
WHERE user_id = 3  -- Change this to your user_id
ORDER BY created_at DESC;

-- ============================================
-- VIEW FLUENCY SCORES
-- ============================================

-- View fluency improvements
SELECT 
    fs.score_id,
    ah.original_filename,
    u.name AS user_name,
    fs.before_score,
    fs.after_score,
    fs.improvement_score,
    fs.repetition_count_before,
    fs.repetition_count_after,
    fs.filler_count_before,
    fs.filler_count_after,
    fs.created_at
FROM fluency_scores fs
JOIN audio_history ah ON fs.audio_id = ah.audio_id
JOIN users u ON ah.user_id = u.user_id
ORDER BY fs.improvement_score DESC
LIMIT 20;

-- ============================================
-- VIEW USER SESSIONS
-- ============================================

-- View active user sessions
SELECT 
    us.session_id,
    u.name,
    u.email,
    us.expires_at,
    us.created_at,
    us.is_active,
    us.ip_address
FROM user_sessions us
JOIN users u ON us.user_id = u.user_id
WHERE us.is_active = TRUE
ORDER BY us.created_at DESC;

-- ============================================
-- VIEW SYSTEM SETTINGS
-- ============================================

-- View all system settings
SELECT * FROM system_settings;

-- ============================================
-- DATABASE STATISTICS
-- ============================================

-- Count users by role
SELECT 
    role,
    COUNT(*) AS user_count
FROM users
GROUP BY role;

-- Count audio files by output mode
SELECT 
    output_mode,
    COUNT(*) AS count
FROM audio_history
GROUP BY output_mode;

-- Total audio processing statistics
SELECT 
    COUNT(*) AS total_files,
    SUM(file_size_mb) AS total_size_mb,
    AVG(processing_duration) AS avg_duration_sec,
    MIN(created_at) AS first_upload,
    MAX(created_at) AS last_upload
FROM audio_history;

-- User activity summary
SELECT 
    u.user_id,
    u.name,
    u.email,
    u.role,
    COUNT(ah.audio_id) AS files_processed,
    SUM(ah.file_size_mb) AS total_mb_processed,
    MAX(ah.created_at) AS last_activity
FROM users u
LEFT JOIN audio_history ah ON u.user_id = ah.user_id
GROUP BY u.user_id, u.name, u.email, u.role
ORDER BY files_processed DESC;

-- ============================================
-- SEARCH QUERIES
-- ============================================

-- Find user by email
SELECT * FROM users WHERE email = 'admin@speechclarity.com';

-- Find user by name (partial match)
SELECT * FROM users WHERE name LIKE '%Shrinivas%';

-- Find audio files by filename
SELECT * FROM audio_history WHERE original_filename LIKE '%hello%';

-- ============================================
-- USEFUL MANAGEMENT QUERIES
-- ============================================

-- Check if email exists
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM users WHERE email = 'test@example.com')
        THEN 'Email exists'
        ELSE 'Email available'
    END AS email_status;

-- View users who never logged in
SELECT 
    user_id,
    name,
    email,
    created_at
FROM users
WHERE last_login IS NULL;

-- View premium users
SELECT 
    user_id,
    name,
    email,
    role,
    created_at
FROM users
WHERE role IN ('PREMIUM', 'ADMIN');

-- ============================================
-- TABLE STRUCTURE QUERIES
-- ============================================

-- Show all tables in database
SHOW TABLES;

-- Describe users table structure
DESCRIBE users;

-- Describe audio_history table structure
DESCRIBE audio_history;

-- Show table creation statement
SHOW CREATE TABLE users;

-- ============================================
-- QUICK REFERENCE
-- ============================================

-- Database name: AI_Speech
-- Admin credentials:
--   Email: admin@speechclarity.com
--   Password: admin123

-- Your user credentials:
--   Email: shrinivassondur03@gmail.com
--   Password: (whatever you registered with)

-- Note: Passwords are hashed with bcrypt in the database
-- You cannot see plain text passwords for security reasons

-- ============================================
-- END OF QUERIES
-- ============================================
