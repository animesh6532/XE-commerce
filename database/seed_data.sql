-- Seed Data for Aura-Commerce-AI (Xecomerce)
-- Author: Senior Database Engineer & Architect
-- Matches MySQL schema in database/ecommerce.sql

-- Clear any existing seed records (handled via schema reset, but added here for safety)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `search_history`;
TRUNCATE TABLE `model_predictions`;
TRUNCATE TABLE `recommendations_logs`;
TRUNCATE TABLE `chatbot_logs`;
TRUNCATE TABLE `user_activity`;
TRUNCATE TABLE `ratings`;
TRUNCATE TABLE `reviews`;
TRUNCATE TABLE `order_items`;
TRUNCATE TABLE `orders`;
TRUNCATE TABLE `wishlist`;
TRUNCATE TABLE `cart_items`;
TRUNCATE TABLE `carts`;
TRUNCATE TABLE `users`;
TRUNCATE TABLE `products`;
TRUNCATE TABLE `categories`;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. Seed Categories
-- -----------------------------------------------------------------------------
INSERT INTO `categories` (`id`, `name`, `description`) VALUES
(1, 'Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|USBCables', 'High speed charging and sync cables'),
(2, 'Computers&Accessories|Accessories&Peripherals|Keyboards', 'Mechanical and wireless keyboards'),
(3, 'Electronics|HomeTheater,TV&Video|Accessories|Cables|HDMICables', 'HDMI cables and connectors'),
(4, 'Electronics|HomeAudio|Headphones', 'In-ear, over-ear and wireless headphones');

-- -----------------------------------------------------------------------------
-- 2. Seed Products
-- -----------------------------------------------------------------------------
INSERT INTO `products` (`id`, `product_code`, `category_id`, `name`, `description`, `actual_price`, `discounted_price`, `stock_quantity`, `image_url`, `product_link`) VALUES
(1, 'B07JW9H4J1', 1, 'Wayona Nylon Braided USB to Lightning Fast Charging and Data Sync Cable', 'High Compatibility: Compatible with iPhone 13, 12, 11, X, 8, 7, 6, 5, iPad. Durable nylon braided design.', 1399.00, 399.00, 150, 'https://m.media-amazon.com/images/I/51UsScvHQNL._SX300_SY300_QL70_FMwebp_.jpg', 'https://www.amazon.in/dp/B07JW9H4J1'),
(2, 'B098NS6PVG', 1, 'Ambrane Unbreakable 60W / 3A Fast Charging 1.5m Braided Type C Cable', 'Supports Quick Charging 3.0 and PD Technology. Unbreakable braided outer jacket.', 1199.00, 349.00, 200, 'https://m.media-amazon.com/images/I/31zOsqQOAOL._SY445_SX342_QL70_FMwebp_.jpg', 'https://www.amazon.in/dp/B098NS6PVG'),
(3, 'B08HQ815W8', 2, 'Keychron K2 Version 2 Wireless Mechanical Keyboard (84 Keys)', 'Gateron G Pro Mechanical switches, RGB Backlight, aluminum frame, Bluetooth/Wired connectivity.', 9999.00, 7499.00, 35, 'https://m.media-amazon.com/images/I/61Nl-qXfU8L._SX466_.jpg', 'https://www.amazon.in/dp/B08HQ815W8'),
(4, 'B014I8SSD0', 3, 'AmazonBasics High-Speed HDMI Cable - 6 Feet (2-Pack)', 'Supports Ethernet, 3D, 4K video and Audio Return Channel (ARC). Black jacket.', 1500.00, 799.00, 300, 'https://m.media-amazon.com/images/I/619t9p9328L._SX466_.jpg', 'https://www.amazon.in/dp/B014I8SSD0'),
(5, 'B07F2DTTNB', 4, 'Sennheiser HD 450SE Wireless Headphones with Active Noise Cancellation', 'Alexa integrated, Bluetooth 5.0, 30-hour battery life, AAC and aptX Low Latency support.', 14990.00, 8990.00, 45, 'https://m.media-amazon.com/images/I/61-gK4zI7nL._SX466_.jpg', 'https://www.amazon.in/dp/B07F2DTTNB');

-- -----------------------------------------------------------------------------
-- 3. Seed Users
-- -----------------------------------------------------------------------------
-- Passwords: All accounts use 'Password123' hashed with bcrypt:
-- Hash: '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a'
INSERT INTO `users` (`id`, `user_uuid`, `email`, `password_hash`, `first_name`, `last_name`, `role`) VALUES
(1, 'USR_ADMIN_001', 'admin@auracommerce.com', '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a', 'System', 'Administrator', 'admin'),
(2, 'USR_SELLER_001', 'seller@auracommerce.com', '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a', 'TechStore', 'Seller', 'seller'),
(3, 'AG3D6O4STAQKAY2UVGEUV46KN35Q', 'customer1@gmail.com', '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a', 'Manav', 'Sharma', 'customer'),
(4, 'AHMY5CWJMMK5BJRBBSNLYT3ONILA', 'customer2@gmail.com', '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a', 'Adarsh', 'Gupta', 'customer'),
(5, 'AHCTC6ULH4XB6YHDY6PCH2R772LQ', 'customer3@gmail.com', '$2b$12$N9qo8uLOqpGC12XqT9C6Eu4EexK6GqK/k2x2Ua8LwQ17y2B3b/O.a', 'Sundeep', 'Kumar', 'customer');

-- -----------------------------------------------------------------------------
-- 4. Seed Carts & Cart Items
-- -----------------------------------------------------------------------------
INSERT INTO `carts` (`id`, `user_id`) VALUES
(1, 3), -- Manav
(2, 4), -- Adarsh
(3, 5); -- Sundeep

INSERT INTO `cart_items` (`cart_id`, `product_id`, `quantity`) VALUES
(1, 2, 2), -- Manav has 2x Ambrane cables
(1, 3, 1), -- Manav has 1x Keychron K2
(2, 4, 1), -- Adarsh has 1x HDMI cable
(3, 5, 1); -- Sundeep has 1x Sennheiser HD 450SE

-- -----------------------------------------------------------------------------
-- 5. Seed Wishlist
-- -----------------------------------------------------------------------------
INSERT INTO `wishlist` (`user_id`, `product_id`) VALUES
(3, 5), -- Manav wishes for Sennheiser HD 450SE
(4, 3); -- Adarsh wishes for Keychron K2

-- -----------------------------------------------------------------------------
-- 6. Seed Orders & Order Items
-- -----------------------------------------------------------------------------
INSERT INTO `orders` (`id`, `order_uuid`, `user_id`, `order_purchase_timestamp`, `status`, `total_amount`, `shipping_address`, `payment_method`, `payment_status`) VALUES
(1, 'ORD_001_846283', 3, '2026-06-01 10:30:00', 'delivered', 8298.00, 'Flat 102, Shanti Vihar, New Delhi, Delhi - 110001', 'Credit Card', 'paid'),
(2, 'ORD_002_746282', 4, '2026-06-05 14:15:00', 'delivered', 349.00, '42-C, Sector 15, Noida, Uttar Pradesh - 201301', 'UPI', 'paid'),
(3, 'ORD_003_192847', 5, '2026-06-10 09:00:00', 'delivered', 1598.00, 'B-4, Hill View Apartments, Bangalore, Karnataka - 560001', 'Cash On Delivery', 'paid');

INSERT INTO `order_items` (`order_id`, `product_id`, `quantity`, `price`) VALUES
(1, 3, 1, 7499.00), -- Keychron K2
(1, 1, 2, 399.00),  -- Wayona cable (x2)
(2, 2, 1, 349.00),  -- Ambrane cable
(3, 4, 2, 799.00);  -- HDMI Cable (x2)

-- -----------------------------------------------------------------------------
-- 7. Seed Reviews (will fire triggers to populate `ratings` and product rating/rating_count)
-- -----------------------------------------------------------------------------
INSERT INTO `reviews` (`review_uuid`, `user_id`, `product_id`, `review_title`, `review_text`, `rating`, `sentiment`, `is_fake`, `fake_probability`) VALUES
('REV_001', 3, 1, 'Satisfied', 'Looks durable. Charging is fine too, no complaints.', 5, 'Positive', FALSE, 0.0210),
('REV_002', 4, 1, 'Charging is really fast', 'Charging is really fast, good product.', 4, 'Positive', FALSE, 0.0532),
('REV_003', 5, 1, 'Value for money', 'Till now satisfied with the quality.', 4, 'Positive', FALSE, 0.0150),
('REV_004', 3, 2, 'Super cable', 'Unbreakable braided Type C cable. Supports fast charging.', 5, 'Positive', FALSE, 0.0054),
('REV_005', 4, 2, 'Good quality for the price', 'Bought for my phone. Fast charging works, nice length.', 4, 'Positive', FALSE, 0.0421),
('REV_006', 5, 3, 'Incredible Wireless Mechanical Keyboard', 'Keychron K2 is amazing. Nice tactile typing sound, beautiful RGB lights.', 5, 'Positive', FALSE, 0.0084),
('REV_007', 3, 5, 'Terrible connection dropouts', 'Frequently disconnects from my phone. Bass is also mud. Dissatisfied.', 2, 'Negative', FALSE, 0.0125),
('REV_008', 4, 5, 'Okay product, not worth the price tag', 'Active noise cancellation is decent but music quality is average.', 3, 'Neutral', TRUE, 0.8950); -- Marked as fake review for demonstration

-- -----------------------------------------------------------------------------
-- 8. Seed User Activity
-- -----------------------------------------------------------------------------
INSERT INTO `user_activity` (`user_id`, `activity_type`, `product_id`, `query`, `metadata`) VALUES
(3, 'view_product', 1, NULL, '{"source": "direct", "duration_seconds": 45}'),
(3, 'add_to_cart', 2, NULL, '{"source": "recommendations"}'),
(3, 'search', NULL, 'mechanical keyboard under 10000', '{"device": "mobile"}'),
(3, 'view_product', 3, NULL, '{"source": "search_results"}'),
(4, 'view_product', 5, NULL, '{"source": "direct"}'),
(5, 'view_product', 4, NULL, '{"source": "direct"}');

-- -----------------------------------------------------------------------------
-- 9. Seed Chatbot Logs
-- -----------------------------------------------------------------------------
INSERT INTO `chatbot_logs` (`user_id`, `query`, `response`, `source`, `routed_dataset`) VALUES
(3, 'I need a fast charging lightning cable.', 'Here are the recommended cables: Wayona Nylon Braided USB to Lightning Charging Cable (₹399.00, rated 4.3). It is currently in stock.', 'ollama', 'USBCables'),
(3, 'Keychron K2 vs Royal Kludge RK84?', 'The Keychron K2 (₹7499) has Gateron G Pro switches and premium aluminum build, whereas the RK84 is slightly cheaper but features a plastic body. Keychron is highly recommended.', 'comparison_engine', 'Keyboards');

-- -----------------------------------------------------------------------------
-- 10. Seed Recommendations Logs
-- -----------------------------------------------------------------------------
INSERT INTO `recommendations_logs` (`user_id`, `recommended_product_ids`, `recommendation_type`, `clicked_product_id`) VALUES
(3, '2,3,5', 'hybrid', 2),
(4, '3,5', 'content_based', NULL),
(5, '1,4', 'collaborative', 4);

-- -----------------------------------------------------------------------------
-- 11. Seed Model Predictions
-- -----------------------------------------------------------------------------
INSERT INTO `model_predictions` (`model_name`, `input_features`, `predicted_output`, `actual_output`) VALUES
('price_predictor', '{"category": "Keyboards", "discounted_price": 7499, "discount_percentage": 25, "rating": 5.0, "rating_count": 1}', '{"predicted_actual_price": 9850.50}', '{"actual_price": 9999.00}'),
('demand_forecast', '{"day_number": 10, "day_of_week": 4, "month": 6, "week_of_year": 23}', '{"predicted_daily_orders": 12}', '{"actual_daily_orders": 14}');

-- -----------------------------------------------------------------------------
-- 12. Seed Search History
-- -----------------------------------------------------------------------------
INSERT INTO `search_history` (`user_id`, `query`, `search_type`, `results_count`) VALUES
(3, 'usb cable', 'keyword', 2),
(3, 'lightning charging cable', 'voice', 1),
(4, 'mechanical keyboard', 'keyword', 1),
(5, 'anc headphones', 'keyword', 1);
