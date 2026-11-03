CREATE DATABASE IF NOT EXISTS influencer_db;
USE influencer_db;

-- Drop tables in reverse order of dependencies to avoid foreign key errors
DROP TABLE IF EXISTS SOCIAL_MEDIA_ITEM;
DROP TABLE IF EXISTS CAMPAIGN_INFLUENCER;
DROP TABLE IF EXISTS CAMPAIGN;
DROP TABLE IF EXISTS PRODUCT;
DROP TABLE IF EXISTS CONTACT;
DROP TABLE IF EXISTS INFLUENCER_CATEGORY;
DROP TABLE IF EXISTS INFLUENCER;
DROP TABLE IF EXISTS CATEGORY;
DROP TABLE IF EXISTS ADMIN;

-- --------------------------------------------------------
-- Table structure for table `admin`
-- --------------------------------------------------------
CREATE TABLE ADMIN (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'admin',
  status VARCHAR(20) NOT NULL DEFAULT 'Active',
  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- Table structure for table `category`
-- --------------------------------------------------------
CREATE TABLE CATEGORY (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(100) UNIQUE NOT NULL
);

-- --------------------------------------------------------
-- Table structure for table `influencer`
-- --------------------------------------------------------
CREATE TABLE INFLUENCER (
  influencer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  bio TEXT,
  follower_count INT DEFAULT 0,
  engagement_rate FLOAT DEFAULT 0.0,
  registration_status VARCHAR(50) DEFAULT 'Active',
  policy_agreed BOOLEAN DEFAULT FALSE,
  policy_agreed_date DATE,
  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  image_url VARCHAR(500) DEFAULT 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='
);

-- --------------------------------------------------------
-- Table structure for table `influencer_category`
-- --------------------------------------------------------
CREATE TABLE INFLUENCER_CATEGORY (
  influencer_id INT NOT NULL,
  category_id INT NOT NULL,
  PRIMARY KEY (influencer_id, category_id),
  FOREIGN KEY (influencer_id) REFERENCES INFLUENCER(influencer_id) ON DELETE CASCADE,
  FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- Table structure for table `contact`
-- --------------------------------------------------------
CREATE TABLE CONTACT (
  contact_id INT AUTO_INCREMENT PRIMARY KEY,
  influencer_id INT,
  contact_type VARCHAR(50),
  contact_value VARCHAR(150),
  last_contacted_date DATE,
  status VARCHAR(50),
  FOREIGN KEY (influencer_id) REFERENCES INFLUENCER(influencer_id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- Table structure for table `product`
-- --------------------------------------------------------
CREATE TABLE PRODUCT (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  created_by INT,
  product_name VARCHAR(150) NOT NULL,
  category VARCHAR(100),
  contact_email VARCHAR(100),
  contact_phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  image_url VARCHAR(500) DEFAULT 'https://cdn-icons-png.flaticon.com/512/679/679720.png',
  FOREIGN KEY (created_by) REFERENCES ADMIN(admin_id) ON DELETE SET NULL
);

-- --------------------------------------------------------
-- Table structure for table `campaign`
-- --------------------------------------------------------
CREATE TABLE CAMPAIGN (
  campaign_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT,
  created_by INT,
  campaign_name VARCHAR(150) NOT NULL,
  start_date DATE,
  end_date DATE,
  budget DECIMAL(12,2),
  objective TEXT,
  status VARCHAR(50) DEFAULT 'Draft',
  FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES ADMIN(admin_id) ON DELETE SET NULL
);

-- --------------------------------------------------------
-- Table structure for table `campaign_influencer`
-- --------------------------------------------------------
CREATE TABLE CAMPAIGN_INFLUENCER (
  campaign_influencer_id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT,
  influencer_id INT,
  agreed_rate DECIMAL(10,2),
  deliverable_date DATE,
  status VARCHAR(50) DEFAULT 'Pending',
  FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN(campaign_id) ON DELETE CASCADE,
  FOREIGN KEY (influencer_id) REFERENCES INFLUENCER(influencer_id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- Table structure for table `social_media_item`
-- --------------------------------------------------------
CREATE TABLE SOCIAL_MEDIA_ITEM (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_influencer_id INT,
  platform_name VARCHAR(50),
  handle VARCHAR(100),
  content_type VARCHAR(50),
  content_url VARCHAR(255),
  posted_date DATE,
  reach INT DEFAULT 0,
  likes_count INT DEFAULT 0,
  shares_count INT DEFAULT 0,
  comments_count INT DEFAULT 0,
  engagement_rate FLOAT DEFAULT 0.0,
  recorded_date DATE,
  FOREIGN KEY (campaign_influencer_id) REFERENCES CAMPAIGN_INFLUENCER(campaign_influencer_id) ON DELETE CASCADE
);

-- ========================================================
-- INSERTING DUMP DATA
-- ========================================================

-- Admin Data
INSERT INTO ADMIN (admin_id, name, email, password, role, status, registered_at) VALUES 
(1, 'System Admin', 'admin@system.com', 'placeholder_will_be_reset', 'admin', 'Active', '2024-01-01 09:00:00'),
(2, 'Sarah Manager', 'sarah@system.com', 'placeholder', 'staff', 'Active', '2024-02-15 10:30:00'),
(3, 'David Coordinator', 'david@system.com', 'placeholder', 'staff', 'Active', '2024-03-20 14:15:00'),
(4, 'Priya Analyst', 'priya@system.com', 'placeholder', 'staff', 'Active', '2024-04-10 11:45:00'),
(7, 'aa', 'aa@gmail.com', 'placeholder', 'staff', 'Active', '2026-10-14 16:38:50'),
(8, 'Joe', 'joe@gmail.com', 'placeholder', 'staff', 'Active', '2026-10-21 11:50:27');

-- Category Data
INSERT INTO CATEGORY (category_id, category_name) VALUES 
(1, 'Fashion'), (2, 'Tech'), (3, 'Fitness'), (4, 'Travel'), 
(5, 'Food'), (6, 'Gaming'), (7, 'Beauty'), (8, 'Lifestyle');

-- Influencer Data (WITH UPDATED LOCAL IMAGE URLS)
INSERT INTO INFLUENCER (influencer_id, name, bio, follower_count, engagement_rate, registration_status, policy_agreed, policy_agreed_date, registered_at, image_url) VALUES
(1, 'Alex Tech', 'Tech reviewer and gadget enthusiast. Reviews smartphones, laptops and accessories.', 150000, 4.5, 'Active', 1, '2024-01-05', '2024-01-05 10:00:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(2, 'FitLife Sarah', 'Certified personal trainer sharing daily workouts and nutrition tips.', 85000, 6.2, 'Active', 1, '2024-01-12', '2024-01-12 11:30:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(3, 'Travel with Mike', 'Exploring hidden gems around the world. 45 countries and counting.', 220000, 3.8, 'Pending', 0, NULL, '2024-02-01 14:20:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(4, 'Foodie Emma', 'Trying out the best street food and restaurants across the globe.', 45000, 7.1, 'Active', 1, '2024-02-08', '2024-02-08 09:15:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(5, 'GamerX', 'Streaming FPS games and tech setups. Twitch partner and esports fan.', 310000, 2.9, 'Active', 1, '2024-02-15', '2024-02-15 16:45:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(6, 'Beauty By Nina', 'Skincare and makeup tutorials. Cruelty-free product reviews.', 125000, 5.4, 'Active', 1, '2024-03-01', '2024-03-01 12:00:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(7, 'Style with Jake', 'Mens fashion and streetwear. Sneaker collector and stylist.', 95000, 4.8, 'Active', 1, '2024-03-10', '2024-03-10 15:30:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(8, 'Wanderlust Anna', 'Solo female traveler documenting budget adventures in Asia.', 180000, 5.9, 'Active', 1, '2024-03-18', '2024-03-18 10:45:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(9, 'Chef Marco', 'Italian chef sharing authentic recipes and restaurant reviews.', 67000, 6.8, 'Active', 1, '2024-04-02', '2024-04-02 13:20:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(11, 'Yoga with Yuki', 'Mindfulness, yoga, and wellness for busy professionals.', 78000, 5.5, 'Active', 1, '2024-04-25', '2024-04-25 17:30:00', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(14, 'Techy Tina 1', 'ddss', 121212, 12.0, 'Active', 1, '2026-10-13', '2026-10-13 11:49:13', 'https://ui-avatars.com/api/?background=fee2e2&color=991b1b&size=150&name='),
(16, 'Techy Tina 2', '', 122222, 12.0, 'Active', 1, '2026-10-14', '2026-10-14 16:39:23', 'd24ed5a2_test.jpg'),
(17, 'Joe', '', 4000, 5.5, 'Active', 1, '2026-10-21', '2026-10-21 10:51:57', 'e50aafd0_test.jpg'),
(18, 'ddd', 'fsa', 32342, 3.0, 'Pending', 1, '2026-10-21', '2026-10-21 12:11:22', '4d01e321_test.jpg');

-- Influencer Category Data
INSERT INTO INFLUENCER_CATEGORY (influencer_id, category_id) VALUES
(6, 1), (7, 1), (1, 2), (5, 2), (18, 2), (2, 3), (11, 3), (3, 4), (8, 4), 
(4, 5), (9, 5), (1, 6), (5, 6), (16, 6), (6, 7), (11, 7), (14, 7), (17, 7), 
(2, 8), (4, 8), (8, 8), (11, 8);

-- Contact Data
INSERT INTO CONTACT (contact_id, influencer_id, contact_type, contact_value, last_contacted_date, status) VALUES
(1, 1, 'Email', 'alex@techreviews.com', '2024-05-10', 'Replied'),
(2, 2, 'Instagram DM', '@fitlifesarah', '2024-05-12', 'Contacted'),
(3, 3, 'Email', 'mike@travelwithmike.com', '2024-05-01', 'No Response'),
(4, 4, 'Email', 'emma@foodieemma.com', '2024-05-08', 'Replied'),
(5, 5, 'Twitter DM', '@gamerx_official', '2024-05-15', 'Contacted'),
(6, 6, 'Instagram DM', '@beautybynina', '2024-05-18', 'Replied'),
(7, 7, 'Email', 'jake@stylewithjake.com', '2024-05-20', 'Contacted'),
(8, 8, 'Instagram DM', '@wanderlustanna', '2024-05-22', 'Replied'),
(9, 9, 'Email', 'marco@chefmarco.it', '2024-05-25', 'No Response'),
(11, 11, 'Instagram DM', '@yogawithyuki', '2024-06-01', 'Contacted'),
(13, 1, 'Phone', '+1-555-0100', '2024-06-05', 'Replied'),
(14, 6, 'Email', 'nina@beautybynina.com', '2024-06-08', 'Contacted'),
(15, 8, 'Email', 'anna@wanderlustanna.com', '2024-06-10', 'Replied'),
(17, 14, 'Phone', '10000', '2026-10-13', 'New'),
(19, 16, 'Phone', '10000', '2026-10-14', 'New'),
(20, 17, 'Instagram DM', 'joe@gmail.com', '2026-10-21', 'New'),
(21, 18, 'Phone', 'dd@gmth.com', '2026-10-21', 'New');

-- Product Data (WITH UPDATED IMAGE URLS)
INSERT INTO PRODUCT (product_id, created_by, product_name, category, contact_email, contact_phone, created_at, image_url) VALUES
(1, 1, 'UltraBook Pro 15', 'Electronics', 'sales@ultrabook.com', '+1-555-0101', '2024-01-20 10:00:00', 'https://p2-ofp.static.pub/ShareResource/optimized/pdp/thinkbook/thinkbook-series/len101b0062/lenovo-thinkbook-16-gen-9-16-intel-pdp-hero.png?width=1200&height=1200'),
(2, 1, 'Organic Whey Protein', 'Health', 'support@organicwhey.com', '+1-555-0102', '2024-02-05 11:30:00', 'https://m.media-amazon.com/images/I/71IW+6OMs2L._AC_SL1080_.jpg'),
(3, 1, 'Smart Fitness Band X2', 'Wearables', 'hello@smartband.com', '+1-555-0103', '2024-02-20 14:00:00', 'https://m.media-amazon.com/images/I/61aQi858dhL._SX679_.jpg'),
(4, 2, 'GlowUp Skincare Kit', 'Beauty', 'care@glowup.com', '+1-555-0104', '2024-03-10 09:15:00', 'https://media.thebodyshop.in/media/catalog/product/g/l/glow_edit.jpg'),
(5, 2, 'TrailBlazer Sneakers', 'Fashion', 'shop@trailblazer.com', '+1-555-0105', '2024-04-01 13:45:00', 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcQd9sc5j4OvphTY7V4mmf7uzmTfhbeu4A2XwTOn6aYzBsIQYMlonvgTXmV_VPL8ciXsDZMOgJK8eciMSUgwnxAttL7oQA_BtxA53khSu6rh3EaaH7ZwR16H'),
(6, 3, 'ProGamer Headset 7.1', 'Gaming', 'team@progamer.com', '+1-555-0106', '2024-04-15 16:20:00', 'https://m.media-amazon.com/images/I/61bgnFyNvaL._AC_SL1500_.jpg');

-- Campaign Data
INSERT INTO CAMPAIGN (campaign_id, product_id, created_by, campaign_name, start_date, end_date, budget, objective, status) VALUES
(1, 1, 1, 'Summer Tech Launch 2024', '2024-06-01', '2024-07-01', 5000.00, 'Generate 1M impressions for UltraBook Pro 15', 'Active'),
(2, 2, 1, 'Fitness Challenge 2024', '2024-06-15', '2024-08-15', 3500.00, 'Drive 500 sign-ups for protein subscription', 'Active'),
(3, 3, 2, 'SmartBand Holiday Promo', '2024-11-01', '2024-12-31', 8000.00, 'Holiday sales boost for Smart Fitness Band X2', 'Draft'),
(4, 4, 2, 'GlowUp Summer Campaign', '2024-06-20', '2024-08-20', 4200.00, 'Increase GlowUp Kit sales by 25% in summer', 'Active'),
(5, 5, 3, 'TrailBlazer Street Style', '2024-07-01', '2024-09-01', 3800.00, 'Position TrailBlazer as the go-to street sneaker', 'Active'),
(6, 6, 3, 'ProGamer Tournament Promo', '2024-08-01', '2024-10-01', 6000.00, 'Sponsor 3 esports tournaments and boost headset sales', 'Draft');

-- Campaign Influencer Data
INSERT INTO CAMPAIGN_INFLUENCER (campaign_influencer_id, campaign_id, influencer_id, agreed_rate, deliverable_date, status) VALUES
(1, 1, 1, 1500.00, '2024-06-15', 'Completed'),
(2, 1, 5, 1200.00, '2024-06-20', 'In Progress'),
(4, 2, 2, 800.00, '2024-07-01', 'Confirmed'),
(5, 2, 4, 600.00, '2024-07-05', 'In Progress'),
(6, 2, 11, 500.00, '2024-07-10', 'Pending'),
(7, 4, 6, 1100.00, '2024-07-05', 'In Progress'),
(8, 4, 7, 700.00, '2024-07-10', 'Confirmed'),
(9, 4, 11, 550.00, '2024-07-15', 'Pending'),
(10, 5, 7, 950.00, '2024-07-20', 'In Progress'),
(11, 5, 8, 1300.00, '2024-07-25', 'Confirmed'),
(13, 6, 5, 1400.00, '2024-08-15', 'Pending');

-- Social Media Item Data
INSERT INTO SOCIAL_MEDIA_ITEM (item_id, campaign_influencer_id, platform_name, handle, content_type, content_url, posted_date, reach, likes_count, shares_count, comments_count, engagement_rate, recorded_date) VALUES
(1, 1, 'YouTube', '@alextech', 'Long-form Review', '', '2024-06-10', 85000, 4200, 320, 280, 5.65, '2024-06-11'),
(2, 1, 'TikTok', '@alextech', 'Short', '', '2024-06-14', 45000, 3100, 480, 220, 8.44, '2024-06-15'),
(3, 2, 'Twitch', '@gamerx', 'Live Stream', '', '2024-06-18', 145000, 11000, 1500, 890, 9.23, '2024-06-19'),
(5, 4, 'Instagram', '@fitlifesarah', 'Reel', '', '2024-06-25', 28000, 2400, 180, 320, 10.36, '2024-06-26'),
(6, 5, 'TikTok', '@foodieemma', 'Short', '', '2024-07-04', 38000, 2900, 340, 210, 9.08, '2024-07-05'),
(7, 7, 'Instagram', '@beautybynina', 'Reel', '', '2024-06-28', 45000, 4100, 380, 520, 11.11, '2024-06-29'),
(8, 8, 'TikTok', '@stylewithjake', 'Short', '', '2024-07-07', 48000, 3900, 420, 290, 9.6, '2024-07-08'),
(9, 11, 'Instagram', '@wanderlustanna', 'Post', '', '2024-07-22', 55000, 4200, 380, 310, 8.89, '2024-07-23'),
(10, 13, 'YouTube', '@gamerxplays', 'Highlight Reel', '', '2024-08-12', 78000, 4600, 380, 520, 7.05, '2024-08-13');