-- 小型气象站 MySQL 初始化脚本（在树莓派上执行）
-- mysql -u root -p < init.sql

CREATE DATABASE IF NOT EXISTS weather_station
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE weather_station;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 环境数据表
CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature DECIMAL(5,2) NULL,
    humidity DECIMAL(5,2) NULL,
    light_intensity DECIMAL(10,2) NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recorded_at (recorded_at)
);

-- 设备信息表
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_no VARCHAR(50) UNIQUE,
    location VARCHAR(200),
    status VARCHAR(20) DEFAULT 'unknown',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 报警记录表
CREATE TABLE IF NOT EXISTS alarms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    param_name VARCHAR(50) NOT NULL,
    param_value DECIMAL(10,2) NOT NULL,
    threshold_value DECIMAL(10,2) NOT NULL,
    alarm_type VARCHAR(10) NOT NULL,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged TINYINT DEFAULT 0,
    INDEX idx_triggered_at (triggered_at)
);

-- 系统设置表（键值）
CREATE TABLE IF NOT EXISTS settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value VARCHAR(255) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 默认阈值与采集间隔（秒）
INSERT INTO settings (setting_key, setting_value) VALUES
('temp_high', '35'),
('temp_low', '5'),
('humidity_high', '85'),
('humidity_low', '20'),
('light_high', '50000'),
('light_low', '0'),
('collect_interval', '5')
ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);

-- 默认用户请通过应用注册接口创建，或运行: python -m api.seed_user
