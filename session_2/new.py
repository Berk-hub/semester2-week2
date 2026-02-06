import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


DB_PATH = "orders.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def read_sql(conn, query, params=None):
    """Pandas ile güvenli SQL okuma (parametreli)."""
    if params is None:
        params = {}
    return pd.read_sql_query(query, conn, params=params)


# -----------------------------
# Yardımcı: Şemayı hızlı kontrol
# -----------------------------
def show_schema(conn):
    tables = ["customers", "orders", "order_items", "products", "deliveries"]
    for t in tables:
        df = read_sql(conn, f"PRAGMA table_info({t});")
        print(f"\n--- {t} columns ---")
        print(df[["name", "type"]])


# -----------------------------
# LEVEL 1
# -----------------------------
def list_categories(conn):
    q = "SELECT DISTINCT category FROM products ORDER BY category;"
    df = read_sql(conn, q)
    print("\n--- Product categories ---")
    print(df)


def count_customers(conn):
    q = "SELECT COUNT(*) AS total_customers FROM customers;"
    df = read_sql(conn, q)
    print("\n--- Total customers ---")
    print(df)


def orders_for_customer(conn, email):
    q = """
    SELECT
        o.order_id,
        o.order_date,
        o.status AS order_status,
        o.total_amount,
        d.scheduled_date,
        d.delivery_window,
        d.delivery_status,
        d.delivered_date
    FROM customers c
    JOIN orders o
      ON o.customer_id = c.customer_id
    LEFT JOIN deliveries d
      ON d.order_id = o.order_id
    WHERE c.email = :email
    ORDER BY o.order_date DESC;
    """
    df = read_sql(conn, q, {"email": email})
    print(f"\n--- Orders for {email} ---")
    if df.empty:
        print("No orders found for this email.")
    else:
        print(df)


def products_below_2(conn):
    q = """
    SELECT product_id, name, category, price
    FROM products
    WHERE price < 2.0
    ORDER BY price ASC, name;
    """
    df = read_sql(conn, q)
    print("\n--- Products below £2 ---")
    print(df)


# -----------------------------
# LEVEL 2
# -----------------------------
def top_5_spenders(conn):
    q = """
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        SUM(o.total_amount) AS total_spent,
        COUNT(o.order_id) AS num_orders
    FROM customers c
    JOIN orders o
      ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    df = read_sql(conn, q)
    print("\n--- Top 5 spenders ---")
    print(df)


def orders_per_category(conn, plot=True):
    # Not: Bir sipariş birden fazla kategori içeriyorsa, her kategoriye 1 kez sayılır.
    q = """
    SELECT
        p.category,
        COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    JOIN products p
      ON p.product_id = oi.product_id
    GROUP BY p.category
    ORDER BY order_count DESC;
    """
    df = read_sql(conn, q)
    print("\n--- Orders per category (distinct orders) ---")
    print(df)

    if plot and not df.empty:
        ax = df.plot.bar(x="category", y="order_count", legend=False, figsize=(10, 5))
        ax.set_title("Orders per Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Orders")
        plt.tight_layout()
        plt.show()


def avg_products_per_order(conn):
    # Ortalama sepetteki ürün adedi = her order için SUM(quantity) al, sonra AVG
    q = """
    WITH per_order AS (
        SELECT
            order_id,
            SUM(quantity) AS total_items
        FROM order_items
        GROUP BY order_id
    )
    SELECT AVG(total_items) AS avg_items_per_order
    FROM per_order;
    """
    df = read_sql(conn, q)
    print("\n--- Average number of products per order ---")
    print(df)


def deliveries_by_status(conn, plot=True):
    q = """
    SELECT
        delivery_status,
        COUNT(*) AS cnt
    FROM deliveries
    GROUP BY delivery_status
    ORDER BY cnt DESC;
    """
    df = read_sql(conn, q)
    print("\n--- Deliveries by status ---")
    print(df)

    if plot and not df.empty:
        ax = df.set_index("delivery_status")["cnt"].plot.pie(
            autopct="%1.1f%%", startangle=90, figsize=(6, 6)
        )
        ax.set_ylabel("")
        ax.set_title("Delivery Status Distribution")
        plt.tight_layout()
        plt.show()


# -----------------------------
# LEVEL 3
# -----------------------------
def top_10_products_by_quantity(conn):
    q = """
    SELECT
        p.product_id,
        p.name,
        p.category,
        SUM(oi.quantity) AS total_qty
    FROM order_items oi
    JOIN products p
      ON p.product_id = oi.product_id
    GROUP BY p.product_id
    ORDER BY total_qty DESC
    LIMIT 10;
    """
    df = read_sql(conn, q)
    print("\n--- Top 10 products by quantity sold ---")
    print(df)


def revenue_per_category(conn, plot=True):
    q = """
    SELECT
        p.category,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items oi
    JOIN products p
      ON p.product_id = oi.product_id
    GROUP BY p.category
    ORDER BY revenue DESC;
    """
    df = read_sql(conn, q)
    print("\n--- Revenue per category ---")
    print(df)

    if plot and not df.empty:
        ax = df.plot.bar(x="category", y="revenue", legend=False, figsize=(10, 5))
        ax.set_title("Revenue per Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Revenue (£)")
        plt.tight_layout()
        plt.show()


def orders_per_delivery_window(conn, plot=True):
    q = """
    SELECT
        delivery_window,
        COUNT(*) AS orders_count
    FROM deliveries
    GROUP BY delivery_window
    ORDER BY orders_count DESC;
    """
    df = read_sql(conn, q)
    print("\n--- Orders per delivery window ---")
    print(df)

    if plot and not df.empty:
        ax = df.plot.bar(x="delivery_window", y="orders_count", legend=False, figsize=(10, 5))
        ax.set_title("Orders per Delivery Window")
        ax.set_xlabel("Delivery window")
        ax.set_ylabel("Orders")
        plt.tight_layout()
        plt.show()


def top_customers_by_avg_order_value(conn, min_orders=2):
    q = """
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        COUNT(o.order_id) AS num_orders,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value
    FROM customers c
    JOIN orders o
      ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    HAVING COUNT(o.order_id) >= :min_orders
    ORDER BY avg_order_value DESC
    LIMIT 10;
    """
    df = read_sql(conn, q, {"min_orders": min_orders})
    print(f"\n--- Top customers by average order value (min_orders={min_orders}) ---")
    print(df)


def delivery_performance_by_window(conn, plot=True):
    q = """
    SELECT
        delivery_window,
        SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        SUM(CASE WHEN delivery_status = 'failed' THEN 1 ELSE 0 END) AS failed,
        COUNT(*) AS total
    FROM deliveries
    GROUP BY delivery_window
    ORDER BY total DESC;
    """
    df = read_sql(conn, q)
    print("\n--- Delivery performance by time window ---")
    print(df)

    if plot and not df.empty:
        plot_df = df.set_index("delivery_window")[["delivered", "failed"]]
        ax = plot_df.plot(kind="bar", stacked=True, figsize=(10, 5))
        ax.set_title("Delivered vs Failed by Delivery Window")
        ax.set_xlabel("Delivery window")
        ax.set_ylabel("Count")
        plt.tight_layout()
        plt.show()


# -----------------------------
# LEVEL 4 (opsiyonel)
# -----------------------------
def repeat_purchase_rate(conn):
    # Repeat customer: >1 order
    q = """
    WITH counts AS (
        SELECT customer_id, COUNT(*) AS n
        FROM orders
        GROUP BY customer_id
    )
    SELECT
        SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END) AS repeat_customers,
        COUNT(*) AS customers_with_orders,
        ROUND(1.0 * SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS repeat_rate
    FROM counts;
    """
    df = read_sql(conn, q)
    print("\n--- Repeat purchase rate (among customers who ordered) ---")
    print(df)


# -----------------------------
# Basit CLI Dashboard Menü
# -----------------------------
def menu():
    with get_conn() as conn:
        while True:
            print("\n" + "=" * 50)
            print("Leedsburies Supermarket - Mini Dashboard")
            print("=" * 50)
            print("1) List product categories")
            print("2) Count total customers")
            print("3) Show orders for a customer email")
            print("4) List products priced below £2")
            print("5) Top 5 spenders")
            print("6) Orders per category (bar chart)")
            print("7) Average number of products per order")
            print("8) Deliveries by status (pie chart)")
            print("9) Top 10 products by quantity sold")
            print("10) Revenue per category (bar chart)")
            print("11) Orders per delivery window (bar chart)")
            print("12) Top customers by average order value")
            print("13) Delivery performance by window (stacked bar)")
            print("14) Repeat purchase rate (optional)")
            print("15) Show schema (debug)")
            print("0) Exit")

            choice = input("Select: ").strip()

            if choice == "1":
                list_categories(conn)
            elif choice == "2":
                count_customers(conn)
            elif choice == "3":
                email = input("Customer email: ").strip()
                orders_for_customer(conn, email)
            elif choice == "4":
                products_below_2(conn)
            elif choice == "5":
                top_5_spenders(conn)
            elif choice == "6":
                orders_per_category(conn, plot=True)
            elif choice == "7":
                avg_products_per_order(conn)
            elif choice == "8":
                deliveries_by_status(conn, plot=True)
            elif choice == "9":
                top_10_products_by_quantity(conn)
            elif choice == "10":
                revenue_per_category(conn, plot=True)
            elif choice == "11":
                orders_per_delivery_window(conn, plot=True)
            elif choice == "12":
                try:
                    min_orders = int(input("min_orders (default 2): ").strip() or "2")
                except ValueError:
                    min_orders = 2
                top_customers_by_avg_order_value(conn, min_orders=min_orders)
            elif choice == "13":
                delivery_performance_by_window(conn, plot=True)
            elif choice == "14":
                repeat_purchase_rate(conn)
            elif choice == "15":
                show_schema(conn)
            elif choice == "0":
                break
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    menu()