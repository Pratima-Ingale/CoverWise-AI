-- CoverWise AI - Property & Casualty Insurance Database Schema
-- Compatible with XAMPP MySQL (MariaDB) / phpMyAdmin

CREATE DATABASE IF NOT EXISTS `coverwise_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `coverwise_db`;

-- 1. Policies Table (Property & Casualty)
CREATE TABLE IF NOT EXISTS `policies` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `policy_id` VARCHAR(30) NOT NULL UNIQUE,
    `policy_name` VARCHAR(150) NOT NULL,
    `policy_type` VARCHAR(50) NOT NULL,
    `company_name` VARCHAR(100) NOT NULL,
    `min_property_age` INT NOT NULL DEFAULT 0,
    `max_property_age` INT NOT NULL DEFAULT 60,
    `min_property_value` BIGINT NOT NULL DEFAULT 100000,
    `max_property_value` BIGINT NOT NULL DEFAULT 100000000,
    `coverage_amount` BIGINT NOT NULL,
    `annual_premium` DECIMAL(10, 2) NOT NULL,
    `claim_settlement_ratio` DECIMAL(5, 2) NOT NULL,
    `third_party_liability` BIGINT NOT NULL DEFAULT 500000,
    `deductible_amount` INT NOT NULL DEFAULT 2000,
    `fire_perils_covered` VARCHAR(10) DEFAULT 'Yes',
    `natural_calamities_covered` VARCHAR(10) DEFAULT 'Yes',
    `burglary_theft_covered` VARCHAR(10) DEFAULT 'Yes',
    `loss_of_rent_covered` VARCHAR(10) DEFAULT 'Yes',
    `key_features` TEXT,
    `description` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Customers Table (Property Profiles)
CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_name` VARCHAR(100) NOT NULL DEFAULT 'Customer',
    `property_type` VARCHAR(50) NOT NULL DEFAULT 'Homeowners Comprehensive',
    `property_age` INT NOT NULL DEFAULT 5,
    `property_value` BIGINT NOT NULL DEFAULT 5000000,
    `annual_income` BIGINT NOT NULL DEFAULT 1000000,
    `insurance_budget` DECIMAL(10, 2) NOT NULL,
    `required_coverage` BIGINT NOT NULL,
    `priority_preference` VARCHAR(50) DEFAULT 'balanced',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Recommendation History Table
CREATE TABLE IF NOT EXISTS `recommendation_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `recommended_policies_json` JSON NOT NULL,
    `ai_explanation` TEXT,
    `recommended_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_rec_customer` FOREIGN KEY (`customer_id`) 
        REFERENCES `customers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
