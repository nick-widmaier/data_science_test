import sqlite3
import numpy as np
import pandas as pd


def setup_assessment_environment():
    # 1. Setup SQLite DB
    conn = sqlite3.connect("assessment.db")
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id INT PRIMARY KEY,
        customer_name TEXT,
        signup_date DATE
    );

    CREATE TABLE orders (
        order_id INT PRIMARY KEY,
        customer_id INT,
        order_date DATE,
        order_amount DECIMAL(10,2),
        status TEXT
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
    """)
    conn.commit()
    conn.close()

    # 2. Setup Churn Dataset for Python Tasks
    np.random.seed(42)
    n_samples = 300

    df = pd.DataFrame({
        "customer_id": np.arange(1000, 1000 + n_samples),
        "age": np.random.randint(18, 70, size=n_samples),
        "account_length": np.random.randint(1, 48, size=n_samples),
        "monthly_spend": np.random.uniform(10.0, 150.0, size=n_samples),
        "tier": np.random.choice(
            ["Basic", "Premium", "VIP"], size=n_samples, p=[0.5, 0.3, 0.2]
        ),
        "churn": np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]),
    })

    # Add NaNs and Outliers
    df.loc[::12, "monthly_spend"] = np.nan
    df.loc[15, "monthly_spend"] = 1800.0  # Extreme outlier

    df.to_csv("customer_data.csv", index=False)
    print("Environment successfully initialized ('assessment.db', 'customer_data.csv').")


if __name__ == "__main__":
    setup_assessment_environment()