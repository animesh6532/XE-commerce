import sqlite3
import pandas as pd
import os
import random
from datetime import datetime

CSV_PATH = 'ml_models/datasets/products.csv'
DB_PATHS = ['backend/ecommerce.db', 'ecommerce.db']

def clean_price(price_val):
    if pd.isna(price_val):
        return 0.0
    val_str = str(price_val).replace('₹', '').replace(',', '').replace(' ', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def clean_rating(rating_val):
    if pd.isna(rating_val):
        return 4.2
    val_str = str(rating_val).strip()
    try:
        return float(val_str)
    except ValueError:
        return 4.2

def get_brand(name):
    if not name:
        return 'Generic'
    parts = str(name).split()
    if len(parts) > 0:
        # Avoid common words like 'The', 'All', 'New'
        brand = parts[0]
        if brand.lower() in ['the', 'all', 'new', 'a', 'an', 'anti', 'multi'] and len(parts) > 1:
            return parts[1]
        return brand
    return 'Generic'

def seed_db():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    print(f"Reading products CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} products from CSV.")

    for db_path in DB_PATHS:
        print(f"Connecting to database: {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Clear existing products
        print("Clearing existing products...")
        cursor.execute("DELETE FROM products;")
        conn.commit()

        # Prepare products list
        products_to_insert = []
        
        # 1. Insert original products from CSV first
        for idx, row in df.iterrows():
            name = str(row['product_name'])
            description = str(row['about_product']) if not pd.isna(row['about_product']) else ''
            category = str(row['category']) if not pd.isna(row['category']) else 'General'
            brand = get_brand(name)
            price = clean_price(row['discounted_price'])
            if price == 0.0:
                price = clean_price(row['actual_price'])
            if price == 0.0:
                price = 499.0 # fallback price
            stock = random.randint(10, 150)
            rating = clean_rating(row['rating'])
            image_url = str(row['img_link']) if not pd.isna(row['img_link']) else ''
            is_featured = 1 if idx % 20 == 0 else 0
            created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            products_to_insert.append((
                name,
                description,
                category,
                brand,
                price,
                stock,
                rating,
                image_url,
                is_featured,
                created_at
            ))

        # 2. Duplicate to reach 10,000+ products for performance scaling
        original_count = len(products_to_insert)
        target_count = 10500
        print(f"Duplicating original {original_count} products to reach {target_count} products...")
        
        edition_idx = 1
        while len(products_to_insert) < target_count:
            for i in range(original_count):
                if len(products_to_insert) >= target_count:
                    break
                orig = products_to_insert[i]
                
                # Create variation
                new_name = f"{orig[0]} - Edition {edition_idx}"
                new_price = round(orig[4] * random.uniform(0.9, 1.15), 2)
                new_stock = random.randint(5, 120)
                new_rating = min(5.0, round(orig[6] * random.uniform(0.85, 1.05), 1))
                
                products_to_insert.append((
                    new_name,
                    orig[1], # description
                    orig[2], # category
                    orig[3], # brand
                    new_price,
                    new_stock,
                    new_rating,
                    orig[7], # image_url
                    0, # is_featured
                    orig[9]  # created_at
                ))
            edition_idx += 1

        print(f"Inserting {len(products_to_insert)} products into database...")
        cursor.executemany(
            """
            INSERT INTO products (name, description, category, brand, price, stock, rating, image_url, is_featured, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            products_to_insert
        )
        conn.commit()

        # Let's verify counts
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        print(f"Successfully seeded {count} products in {db_path}!")

        # Verify featured count
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_featured = 1;")
        featured_count = cursor.fetchone()[0]
        print(f"Featured products: {featured_count}")

        conn.close()

if __name__ == '__main__':
    seed_db()
