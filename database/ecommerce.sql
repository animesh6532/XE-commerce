-- MySQL 8.0+ E-Commerce Database Schema
-- Project: Aura-Commerce-AI (Xecomerce)
-- Author: Senior Database Engineer & Architect

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `search_history`;
DROP TABLE IF EXISTS `model_predictions`;
DROP TABLE IF EXISTS `recommendations_logs`;
DROP TABLE IF EXISTS `chatbot_logs`;
DROP TABLE IF EXISTS `user_activity`;
DROP TABLE IF EXISTS `ratings`;
DROP TABLE IF EXISTS `reviews`;
DROP TABLE IF EXISTS `order_items`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `wishlist`;
DROP TABLE IF EXISTS `cart_items`;
DROP TABLE IF EXISTS `carts`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- Table: categories
-- Purpose: Holds product taxonomy/category structure
-- -----------------------------------------------------------------------------
CREATE TABLE `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL UNIQUE,
    `description` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_category_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: products
-- Purpose: Core product catalog with prices, stock, and average rating cache
-- -----------------------------------------------------------------------------
CREATE TABLE `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_code` VARCHAR(50) NULL UNIQUE, -- For compatibility with datasets (e.g., ASIN 'B07JW9H4J1')
    `category_id` INT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `actual_price` DECIMAL(10, 2) NOT NULL,
    `discounted_price` DECIMAL(10, 2) NOT NULL,
    `discount_percentage` DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE 
            WHEN `actual_price` > 0 THEN ROUND(((`actual_price` - `discounted_price`) / `actual_price`) * 100, 2)
            ELSE 0.00
        END
    ) STORED,
    `rating` DECIMAL(3, 2) DEFAULT 0.00,
    `rating_count` INT DEFAULT 0,
    `in_stock` BOOLEAN DEFAULT TRUE,
    `stock_quantity` INT NOT NULL DEFAULT 0,
    `image_url` VARCHAR(500) NULL,
    `product_link` VARCHAR(500) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
    CONSTRAINT `chk_actual_price` CHECK (`actual_price` >= 0),
    CONSTRAINT `chk_discounted_price` CHECK (`discounted_price` >= 0),
    CONSTRAINT `chk_price_relation` CHECK (`discounted_price` <= `actual_price`),
    INDEX `idx_product_category` (`category_id`),
    INDEX `idx_product_code` (`product_code`),
    INDEX `idx_product_in_stock` (`in_stock`),
    INDEX `idx_product_price` (`discounted_price`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: users
-- Purpose: User registration and authentication profile
-- -----------------------------------------------------------------------------
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_uuid` VARCHAR(50) NULL UNIQUE, -- For compatibility with external datasets
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `first_name` VARCHAR(100) NULL,
    `last_name` VARCHAR(100) NULL,
    `role` ENUM('admin', 'seller', 'customer') DEFAULT 'customer',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`),
    INDEX `idx_user_uuid` (`user_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: carts
-- Purpose: Represents a user's active shopping cart session
-- -----------------------------------------------------------------------------
CREATE TABLE `carts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_carts_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: cart_items
-- Purpose: Represents products within a user's cart
-- -----------------------------------------------------------------------------
CREATE TABLE `cart_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `cart_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_cart_items_cart` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cart_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `chk_cart_item_quantity` CHECK (`quantity` > 0),
    UNIQUE KEY `uq_cart_product` (`cart_id`, `product_id`),
    INDEX `idx_cart_items_cart` (`cart_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: wishlist
-- Purpose: Stores items flagged by customers for later purchase
-- -----------------------------------------------------------------------------
CREATE TABLE `wishlist` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_wishlist_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_wishlist_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uq_user_wishlist_product` (`user_id`, `product_id`),
    INDEX `idx_wishlist_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: orders
-- Purpose: Stores completed transaction summaries
-- -----------------------------------------------------------------------------
CREATE TABLE `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_uuid` VARCHAR(50) NULL UNIQUE, -- For compatibility with datasets
    `user_id` INT NOT NULL,
    `order_purchase_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(50) NOT NULL DEFAULT 'delivered',
    `total_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `shipping_address` TEXT NULL,
    `payment_method` VARCHAR(50) NULL,
    `payment_status` VARCHAR(50) NOT NULL DEFAULT 'paid',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `chk_order_total` CHECK (`total_amount` >= 0),
    INDEX `idx_order_user` (`user_id`),
    INDEX `idx_order_uuid` (`order_uuid`),
    INDEX `idx_order_purchase_timestamp` (`order_purchase_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: order_items
-- Purpose: Stores product details corresponding to a transaction line item
-- -----------------------------------------------------------------------------
CREATE TABLE `order_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `price` DECIMAL(10, 2) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `chk_order_item_quantity` CHECK (`quantity` > 0),
    CONSTRAINT `chk_order_item_price` CHECK (`price` >= 0),
    INDEX `idx_order_items_order` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: reviews
-- Purpose: Customer feedback text used for sentiment & fake review pipelines
-- -----------------------------------------------------------------------------
CREATE TABLE `reviews` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `review_uuid` VARCHAR(50) NULL UNIQUE, -- For compatibility with datasets
    `user_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `review_title` VARCHAR(255) NULL,
    `review_text` TEXT NOT NULL,
    `rating` INT NOT NULL,
    `sentiment` VARCHAR(20) DEFAULT 'Neutral', -- Positive, Neutral, Negative
    `is_fake` BOOLEAN DEFAULT FALSE,
    `fake_probability` DECIMAL(5, 4) DEFAULT 0.0000,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_reviews_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reviews_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5),
    INDEX `idx_review_product` (`product_id`),
    INDEX `idx_review_user` (`user_id`),
    INDEX `idx_review_uuid` (`review_uuid`),
    INDEX `idx_review_rating` (`rating`),
    INDEX `idx_review_sentiment` (`sentiment`),
    INDEX `idx_review_is_fake` (`is_fake`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: ratings
-- Purpose: Aggregated ratings distribution table (recalculated via triggers)
-- -----------------------------------------------------------------------------
CREATE TABLE `ratings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL UNIQUE,
    `one_star_count` INT NOT NULL DEFAULT 0,
    `two_star_count` INT NOT NULL DEFAULT 0,
    `three_star_count` INT NOT NULL DEFAULT 0,
    `four_star_count` INT NOT NULL DEFAULT 0,
    `five_star_count` INT NOT NULL DEFAULT 0,
    `average_rating` DECIMAL(3, 2) NOT NULL DEFAULT 0.00,
    `total_ratings` INT NOT NULL DEFAULT 0,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_ratings_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: user_activity
-- Purpose: Captures customer activity metrics for recommendations and dashboards
-- -----------------------------------------------------------------------------
CREATE TABLE `user_activity` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `activity_type` VARCHAR(50) NOT NULL, -- 'view_product', 'add_to_cart', 'purchase', 'search', 'click_recommendation'
    `product_id` INT NULL,
    `query` VARCHAR(255) NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `metadata` JSON NULL, -- Flexible structure for additional tracing data
    CONSTRAINT `fk_activity_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_activity_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
    INDEX `idx_activity_user` (`user_id`),
    INDEX `idx_activity_type` (`activity_type`),
    INDEX `idx_activity_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: chatbot_logs
-- Purpose: Traces conversations with the AI Chatbot helper
-- -----------------------------------------------------------------------------
CREATE TABLE `chatbot_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `query` TEXT NOT NULL,
    `response` TEXT NOT NULL,
    `source` VARCHAR(50) NOT NULL DEFAULT 'templates', -- 'ollama' or 'templates'
    `routed_dataset` VARCHAR(100) NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_chatbot_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_chatbot_user` (`user_id`),
    INDEX `idx_chatbot_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: recommendations_logs
-- Purpose: Records recommended products displayed to users and actions taken
-- -----------------------------------------------------------------------------
CREATE TABLE `recommendations_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `recommended_product_ids` TEXT NOT NULL, -- Comma-separated list of product IDs (e.g., '1,2,5,10')
    `recommendation_type` VARCHAR(50) NOT NULL, -- 'hybrid', 'content_based', 'collaborative'
    `clicked_product_id` INT NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_rec_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rec_logs_clicked` FOREIGN KEY (`clicked_product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
    INDEX `idx_rec_logs_user` (`user_id`),
    INDEX `idx_rec_logs_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: model_predictions
-- Purpose: Audit log of ML model predictions (price forecasts, demand, sentiment)
-- -----------------------------------------------------------------------------
CREATE TABLE `model_predictions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `model_name` VARCHAR(100) NOT NULL, -- 'recommender', 'sentiment', 'fake_review', 'demand_forecast', 'price_predictor'
    `input_features` JSON NOT NULL,
    `predicted_output` JSON NOT NULL,
    `actual_output` JSON NULL, -- Filled later for feedback logs / drift metrics
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_model_name` (`model_name`),
    INDEX `idx_model_prediction_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- Table: search_history
-- Purpose: Track search metrics (voice, text, image search query)
-- -----------------------------------------------------------------------------
CREATE TABLE `search_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `query` VARCHAR(255) NOT NULL,
    `search_type` VARCHAR(50) NOT NULL DEFAULT 'keyword', -- 'keyword', 'voice', 'image'
    `results_count` INT DEFAULT 0,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_search_history_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_search_user` (`user_id`),
    INDEX `idx_search_query` (`query`),
    INDEX `idx_search_type` (`search_type`),
    INDEX `idx_search_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- DATABASE TRIGGERS
-- Recalculates product rating aggregates on review insert, update, or delete.
-- -----------------------------------------------------------------------------

DELIMITER //

-- 1. AFTER INSERT TRIGGER on `reviews`
CREATE TRIGGER `after_review_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
    -- Ensure a row exists in `ratings` table for the product
    INSERT INTO `ratings` (`product_id`, `one_star_count`, `two_star_count`, `three_star_count`, `four_star_count`, `five_star_count`, `average_rating`, `total_ratings`)
    VALUES (NEW.`product_id`, 0, 0, 0, 0, 0, 0.00, 0)
    ON DUPLICATE KEY UPDATE `updated_at` = CURRENT_TIMESTAMP;

    -- Update counts and averages in `ratings` table
    UPDATE `ratings`
    SET 
        `one_star_count`   = `one_star_count`   + IF(NEW.`rating` = 1, 1, 0),
        `two_star_count`   = `two_star_count`   + IF(NEW.`rating` = 2, 1, 0),
        `three_star_count` = `three_star_count` + IF(NEW.`rating` = 3, 1, 0),
        `four_star_count`  = `four_star_count`  + IF(NEW.`rating` = 4, 1, 0),
        `five_star_count`  = `five_star_count`  + IF(NEW.`rating` = 5, 1, 0),
        `total_ratings`    = `total_ratings`    + 1,
        `average_rating`   = (
            (`one_star_count` * 1 + `two_star_count` * 2 + `three_star_count` * 3 + `four_star_count` * 4 + `five_star_count` * 5)
            / `total_ratings`
        )
    WHERE `product_id` = NEW.`product_id`;

    -- Update the denormalized fields back in `products` table
    UPDATE `products` p
    JOIN `ratings` r ON p.`id` = r.`product_id`
    SET p.`rating` = r.`average_rating`,
        p.`rating_count` = r.`total_ratings`
    WHERE p.`id` = NEW.`product_id`;
END//

-- 2. AFTER UPDATE TRIGGER on `reviews`
CREATE TRIGGER `after_review_update`
AFTER UPDATE ON `reviews`
FOR EACH ROW
BEGIN
    IF OLD.`rating` <> NEW.`rating` THEN
        -- Recalculate rating aggregates on update
        UPDATE `ratings`
        SET 
            `one_star_count`   = `one_star_count`   - IF(OLD.`rating` = 1, 1, 0) + IF(NEW.`rating` = 1, 1, 0),
            `two_star_count`   = `two_star_count`   - IF(OLD.`rating` = 2, 1, 0) + IF(NEW.`rating` = 2, 1, 0),
            `three_star_count` = `three_star_count` - IF(OLD.`rating` = 3, 1, 0) + IF(NEW.`rating` = 3, 1, 0),
            `four_star_count`  = `four_star_count`  - IF(OLD.`rating` = 4, 1, 0) + IF(NEW.`rating` = 4, 1, 0),
            `five_star_count`  = `five_star_count`  - IF(OLD.`rating` = 5, 1, 0) + IF(NEW.`rating` = 5, 1, 0),
            `average_rating`   = (
                (`one_star_count` * 1 + `two_star_count` * 2 + `three_star_count` * 3 + `four_star_count` * 4 + `five_star_count` * 5)
                / IF(`total_ratings` > 0, `total_ratings`, 1)
            )
        WHERE `product_id` = NEW.`product_id`;

        -- Sync with product table
        UPDATE `products` p
        JOIN `ratings` r ON p.`id` = r.`product_id`
        SET p.`rating` = r.`average_rating`
        WHERE p.`id` = NEW.`product_id`;
    END IF;
END//

-- 3. AFTER DELETE TRIGGER on `reviews`
CREATE TRIGGER `after_review_delete`
AFTER DELETE ON `reviews`
FOR EACH ROW
BEGIN
    -- Update aggregates by removing the rating
    UPDATE `ratings`
    SET 
        `one_star_count`   = GREATEST(0, `one_star_count`   - IF(OLD.`rating` = 1, 1, 0)),
        `two_star_count`   = GREATEST(0, `two_star_count`   - IF(OLD.`rating` = 2, 1, 0)),
        `three_star_count` = GREATEST(0, `three_star_count` - IF(OLD.`rating` = 3, 1, 0)),
        `four_star_count`  = GREATEST(0, `four_star_count`  - IF(OLD.`rating` = 4, 1, 0)),
        `five_star_count`  = GREATEST(0, `five_star_count`  - IF(OLD.`rating` = 5, 1, 0)),
        `total_ratings`    = GREATEST(0, `total_ratings`    - 1),
        `average_rating`   = IF(`total_ratings` > 0, 
            (`one_star_count` * 1 + `two_star_count` * 2 + `three_star_count` * 3 + `four_star_count` * 4 + `five_star_count` * 5) / `total_ratings`, 
            0.00
        )
    WHERE `product_id` = OLD.`product_id`;

    -- Sync back to product
    UPDATE `products` p
    JOIN `ratings` r ON p.`id` = r.`product_id`
    SET p.`rating` = r.`average_rating`,
        p.`rating_count` = r.`total_ratings`
    WHERE p.`id` = OLD.`product_id`;
END//

DELIMITER ;
