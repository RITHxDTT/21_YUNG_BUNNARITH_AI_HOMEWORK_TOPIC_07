CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO products (name, category, price, stock)
VALUES
('ASUS TUF Gaming Laptop', 'laptop', 850.00, 5),
('MacBook Air', 'laptop', 999.00, 0),
('Lenovo IdeaPad', 'laptop', 600.00, 8),

('ASUS ROG Strix G16', 'laptop', 1499.00, 4),
('ASUS TUF Gaming A15', 'laptop', 899.00, 7),
('ASUS Vivobook 15', 'laptop', 649.00, 0),
('Acer Nitro V 15', 'laptop', 799.00, 5),
('Lenovo Legion 5', 'laptop', 1199.00, 3),

('iPhone 16', 'phone', 899.00, 10),
('iPhone 16 Pro', 'phone', 1099.00, 4),
('Samsung Galaxy S25', 'phone', 899.00, 7),
('Samsung Galaxy A56', 'phone', 449.00, 12),

('Keychron K2 Mechanical Keyboard', 'keyboard', 89.00, 8),
('Logitech G Pro X Keyboard', 'keyboard', 149.00, 3),
('Razer BlackWidow V4', 'keyboard', 169.00, 4),

('Logitech G502 Hero', 'mouse', 49.00, 12),
('Logitech G Pro X Superlight', 'mouse', 139.00, 5),
('Razer DeathAdder V3', 'mouse', 69.00, 8),

('ASUS TUF Gaming 24 Inch 165Hz', 'monitor', 229.00, 5),
('LG UltraGear 27 Inch 144Hz', 'monitor', 299.00, 7),
('Samsung Odyssey G5', 'monitor', 329.00, 4),

('HyperX Cloud III', 'headset', 99.00, 8),
('Razer BlackShark V2', 'headset', 109.00, 7),

('PlayStation 5 Slim Disc Edition', 'console', 499.00, 5),
('PlayStation 5 Pro', 'console', 699.00, 2),
('Xbox Series X', 'console', 499.00, 0),
('Nintendo Switch OLED', 'console', 349.00, 9),

('PlayStation DualSense Controller', 'controller', 69.00, 15),
('Xbox Wireless Controller', 'controller', 64.00, 12),

('Samsung 990 Pro 1TB SSD', 'storage', 109.00, 10),
('Samsung 990 Pro 2TB SSD', 'storage', 179.00, 6),
('WD Black SN850X 1TB SSD', 'storage', 99.00, 8),

('Corsair Vengeance 16GB DDR5', 'ram', 59.00, 18),
('Kingston Fury Beast 32GB DDR5', 'ram', 94.00, 7),

('NVIDIA GeForce RTX 4060', 'gpu', 299.00, 7),
('NVIDIA GeForce RTX 4070', 'gpu', 549.00, 4),
('AMD Radeon RX 7800 XT', 'gpu', 499.00, 5),

('AMD Ryzen 5 7600', 'cpu', 199.00, 10),
('AMD Ryzen 7 7800X3D', 'cpu', 399.00, 4),
('Intel Core i7 14700K', 'cpu', 399.00, 5),

('Logitech C920 HD Pro', 'webcam', 79.00, 9),
('HyperX QuadCast S', 'microphone', 159.00, 6),

('USB-C 7-in-1 Hub', 'accessory', 39.00, 20),
('Laptop Cooling Pad', 'accessory', 29.00, 15),
('Gaming Mouse Pad XL', 'accessory', 24.00, 25);