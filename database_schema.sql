-- Speech Clarity Enhancement System - Production Database Schema
-- Database: AI_Speech
-- User: root
-- Password: root

CREATE DATABASE IF NOT EXISTS AI_Speech;
USE AI_Speech;

-- ===================================================
-- 1. USERS TABLE - Authentication & User Management
-- ===================================================
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('normal', 'premium', 'admin') DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
);

-- ===================================================
-- 2. USAGE LOGS TABLE - Track Free vs Premium Usage
-- ===================================================
CREATE TABLE usage_logs (
    usage_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_uses INT DEFAULT 0,
    remaining_uses INT DEFAULT 10, -- Free users get 10 uses
    last_used_at TIMESTAMP NULL,
    reset_date DATE NULL, -- For monthly resets if needed
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_last_used (last_used_at)
);

-- ===================================================
-- 3. SUBSCRIPTIONS TABLE - Premium Plans Management
-- ===================================================
CREATE TABLE subscriptions (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    plan_type ENUM('free', 'monthly_premium', 'yearly_premium') DEFAULT 'free',
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    payment_status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    amount DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_plan_type (plan_type),
    INDEX idx_is_active (is_active),
    INDEX idx_end_date (end_date)
);

-- ===================================================
-- 4. AUDIO HISTORY TABLE - Store Processing Results
-- ===================================================
CREATE TABLE audio_history (
    audio_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    original_audio_path VARCHAR(500) NOT NULL,
    enhanced_audio_path VARCHAR(500) NULL,
    transcript_raw TEXT NULL,
    transcript_cleaned TEXT NULL,
    output_mode ENUM('audio', 'text', 'both') DEFAULT 'both',
    processing_duration DECIMAL(5,2) NULL, -- seconds
    file_size_mb DECIMAL(8,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_output_mode (output_mode)
);

-- ===================================================
-- 5. FLUENCY SCORES TABLE - Before/After Metrics
-- ===================================================
CREATE TABLE fluency_scores (
    score_id INT PRIMARY KEY AUTO_INCREMENT,
    audio_id INT NOT NULL,
    before_score DECIMAL(5,2) NOT NULL,
    after_score DECIMAL(5,2) NOT NULL,
    repetition_count_before INT DEFAULT 0,
    repetition_count_after INT DEFAULT 0,
    filler_count_before INT DEFAULT 0,
    filler_count_after INT DEFAULT 0,
    pause_count_before INT DEFAULT 0,
    pause_count_after INT DEFAULT 0,
    total_words_before INT DEFAULT 0,
    total_words_after INT DEFAULT 0,
    improvement_score DECIMAL(5,2) GENERATED ALWAYS AS (after_score - before_score) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audio_id) REFERENCES audio_history(audio_id) ON DELETE CASCADE,
    INDEX idx_audio_id (audio_id),
    INDEX idx_improvement (improvement_score),
    INDEX idx_before_score (before_score),
    INDEX idx_after_score (after_score)
);

-- ===================================================
-- 6. USER SESSIONS TABLE - JWT Token Management
-- ===================================================
CREATE TABLE user_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    user_agent TEXT NULL,
    ip_address VARCHAR(45) NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active)
);

-- ===================================================
-- 7. SYSTEM SETTINGS TABLE - Admin Configuration
-- ===================================================
CREATE TABLE system_settings (
    setting_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT NULL,
    updated_by INT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_setting_key (setting_key)
);

-- ===================================================
-- INITIAL DATA SETUP
-- ===================================================

-- Default system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('free_usage_limit', '10', 'Number of free enhancements per user'),
('max_file_size_mb', '50', 'Maximum audio file size in MB'),
('max_duration_seconds', '300', 'Maximum audio duration in seconds'),
('monthly_premium_price', '9.99', 'Monthly premium subscription price'),
('yearly_premium_price', '99.99', 'Yearly premium subscription price'),
('system_maintenance', 'false', 'System maintenance mode flag');

-- Create default admin user (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (name, email, password_hash, role, email_verified) VALUES
('System Administrator', 'admin@speechclarity.com', '$2b$12$LQv3c1yqBwlVHpPRrQVe/.VHT/HJL.laVGWWOdFL9ibHqT9B6tbc.', 'admin', TRUE);

-- Create usage log for admin user
INSERT INTO usage_logs (user_id, total_uses, remaining_uses) VALUES
(1, 0, 999999); -- Admin gets unlimited usage

-- Create free subscription for admin
INSERT INTO subscriptions (user_id, plan_type, start_date, is_active) VALUES
(1, 'yearly_premium', CURDATE(), TRUE);

-- ===================================================
-- USEFUL VIEWS FOR REPORTING
-- ===================================================

-- User dashboard view
CREATE VIEW user_dashboard AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    u.role,
    ul.total_uses,
    ul.remaining_uses,
    s.plan_type,
    s.end_date as subscription_end,
    COUNT(ah.audio_id) as total_processed_files,
    AVG(fs.improvement_score) as avg_improvement
FROM users u
LEFT JOIN usage_logs ul ON u.user_id = ul.user_id
LEFT JOIN subscriptions s ON u.user_id = s.user_id AND s.is_active = TRUE
LEFT JOIN audio_history ah ON u.user_id = ah.user_id
LEFT JOIN fluency_scores fs ON ah.audio_id = fs.audio_id
GROUP BY u.user_id, u.name, u.email, u.role, ul.total_uses, ul.remaining_uses, s.plan_type, s.end_date;

-- Admin statistics view
CREATE VIEW admin_stats AS
SELECT 
    COUNT(DISTINCT u.user_id) as total_users,
    COUNT(DISTINCT CASE WHEN u.role = 'premium' THEN u.user_id END) as premium_users,
    COUNT(DISTINCT CASE WHEN u.role = 'normal' THEN u.user_id END) as free_users,
    COUNT(ah.audio_id) as total_processed_files,
    SUM(ah.file_size_mb) as total_storage_mb,
    AVG(ah.processing_duration) as avg_processing_time,
    AVG(fs.improvement_score) as avg_improvement_score
FROM users u
LEFT JOIN audio_history ah ON u.user_id = ah.user_id
LEFT JOIN fluency_scores fs ON ah.audio_id = fs.audio_id;

-- ===================================================
-- INDEXES FOR PERFORMANCE
-- ===================================================

-- Composite indexes for common queries
CREATE INDEX idx_user_active_subscription ON subscriptions(user_id, is_active, end_date);
CREATE INDEX idx_user_recent_history ON audio_history(user_id, created_at DESC);
CREATE INDEX idx_usage_tracking ON usage_logs(user_id, remaining_uses);

-- ===================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ===================================================

-- Trigger to create usage log when user is created
DELIMITER //
CREATE TRIGGER create_usage_log_after_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO usage_logs (user_id, total_uses, remaining_uses) 
    VALUES (NEW.user_id, 0, 10);
END//
DELIMITER ;

-- Trigger to create free subscription when user is created
DELIMITER //
CREATE TRIGGER create_free_subscription_after_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO subscriptions (user_id, plan_type, start_date, is_active) 
    VALUES (NEW.user_id, 'free', CURDATE(), TRUE);
END//
DELIMITER ;

-- Trigger to update last_login when user logs in
DELIMITER //
CREATE TRIGGER update_last_login_after_session_insert
AFTER INSERT ON user_sessions
FOR EACH ROW
BEGIN
    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END//
DELIMITER ;

COMMIT;

-- ===================================================
-- VERIFICATION QUERIES
-- ===================================================
-- Run these to verify the schema was created correctly:

-- SELECT 'Database created successfully' as status;
-- SHOW TABLES;
-- SELECT COUNT(*) as admin_users FROM users WHERE role = 'admin';
-- SELECT * FROM system_settings;
-- SELECT * FROM user_dashboard WHERE role = 'admin';