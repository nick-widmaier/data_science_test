CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    order_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL
);

INSERT INTO customers VALUES 
(1, 'Alice Smith', '2025-01-01'),
(2, 'Bob Jones', '2025-01-15'),
(3, 'Charlie Brown', '2025-02-01'),
(4, 'Diana Prince', '2025-02-10');

INSERT INTO orders VALUES
(101, 1, '2025-01-10', 150.00, 'completed'),
(102, 1, '2025-02-12', 200.00, 'completed'),
(103, 2, '2025-01-20', 500.00, 'completed'),
(104, 3, '2025-02-15', 50.00, 'cancelled'),
(105, 1, '2025-03-01', 300.00, 'completed'),
(106, 2, '2025-03-10', 100.00, 'completed');