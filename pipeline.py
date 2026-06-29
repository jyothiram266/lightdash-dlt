"""
Complete analytics demo: dlt → MotherDuck → dbt → Lightdash

This pipeline:
1. Generates realistic synthetic e-commerce data (customers, products, orders)
2. Loads into MotherDuck (cloud DuckDB) with primary key + foreign key relationships
3. Prepares data for dbt transformation via dlt schema metadata
4. Creates foundation for dbt-native BI in Lightdash

Requirements:
- MOTHERDUCK_TOKEN env variable set
- dlt[duckdb] installed
- faker library for synthetic data
"""

import dlt
import os
from datetime import datetime, timedelta
from faker import Faker
from typing import Iterator, Any
import random


fake = Faker()


# =============================================================================
# DATA GENERATION FUNCTIONS
# =============================================================================

def generate_customers(count: int = 50) -> Iterator[dict[str, Any]]:
    """Generate realistic synthetic customer data."""
    for i in range(1, count + 1):
        yield {
            "id": i,
            "name": fake.name(),
            "email": fake.email(),
            "country": fake.country_code(representation="alpha-2"),
            "signup_date": fake.date_between(start_date="-2y").isoformat(),
        }


def generate_products(count: int = 20) -> Iterator[dict[str, Any]]:
    """Generate realistic synthetic product data."""
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]
    for i in range(1, count + 1):
        yield {
            "id": i,
            "name": fake.word().title() + " " + fake.word().title(),
            "category": random.choice(categories),
            "price": round(random.uniform(9.99, 499.99), 2),
            "created_date": fake.date_between(start_date="-1y").isoformat(),
        }


def generate_orders(
    customers_count: int = 50, 
    products_count: int = 20,
    orders_count: int = 200
) -> Iterator[dict[str, Any]]:
    """
    Generate realistic synthetic order data with FK relationships.
    
    Each order references a valid customer_id and product_id.
    """
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    
    for i in range(1, orders_count + 1):
        customer_id = random.randint(1, customers_count)
        product_id = random.randint(1, products_count)
        quantity = random.randint(1, 5)
        
        yield {
            "id": i,
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity,
            "order_date": fake.date_between(start_date="-6m").isoformat(),
            "status": random.choice(statuses),
        }


# =============================================================================
# dlt RESOURCES - Define data + schema metadata
# =============================================================================

@dlt.resource(
    primary_key="id",
    write_disposition="replace"
)
def customers() -> Iterator[dict[str, Any]]:
    """Load customer data with primary key."""
    yield from generate_customers(count=50)


@dlt.resource(
    primary_key="id",
    write_disposition="replace"
)
def products() -> Iterator[dict[str, Any]]:
    """Load product data with primary key."""
    yield from generate_products(count=20)


@dlt.resource(
    primary_key="id",
    write_disposition="replace"
)
def orders() -> Iterator[dict[str, Any]]:
    """Load order data with primary key and FK relationships."""
    yield from generate_orders(customers_count=50, products_count=20, orders_count=200)


# =============================================================================
# dlt SOURCE - Combine resources + FK relationships
# =============================================================================

@dlt.source(name="sales_analytics_source")
def ecommerce_source():
    """
    E-commerce data source with foreign key relationships.
    
    Relationships:
    - orders.customer_id → customers.id
    - orders.product_id → products.id
    """
    return [customers(), products(), orders()]


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def load_sample_shop():
    """
    Main pipeline entry point.
    
    1. Creates MotherDuck destination connection
    2. Runs pipeline with synthetic data
    3. Prints summary for manual verification
    """
    
    # Get MotherDuck token from environment
    motherduck_token = os.getenv("MOTHERDUCK_TOKEN")
    if not motherduck_token:
        raise ValueError(
            "MOTHERDUCK_TOKEN environment variable not set.\n"
            "Export it: export MOTHERDUCK_TOKEN='your_token_here'"
        )

    # Ensure MotherDuck database exists before starting the pipeline
    import duckdb
    print("Ensuring database 'retail_analytics' exists in MotherDuck...")
    conn = duckdb.connect(f"md:?motherduck_token={motherduck_token}")
    conn.execute("CREATE DATABASE IF NOT EXISTS retail_analytics;")
    conn.close()

    print("\n" + "="*80)
    print("SALES ANALYTICS: dlt → MotherDuck Pipeline")
    print("="*80)
    print(f"📊 Destination: MotherDuck (retail_analytics database)")
    print(f"📂 Dataset: raw")
    print(f"⏱️  Timestamp: {datetime.now().isoformat()}")
    print("="*80 + "\n")
    
    # Create dlt pipeline
    pipeline = dlt.pipeline(
        pipeline_name="sales_analytics_pipeline",
        destination=dlt.destinations.motherduck(
            credentials=f"md:retail_analytics?motherduck_token={motherduck_token}"
        ),
        dataset_name="raw",
    )
    
    # Load data from source
    print("🚀 Loading data...")
    load_info = pipeline.run(
        ecommerce_source(),
        write_disposition="replace",
    )
    
    # Print summary
    print("\n✅ Ingestion completed!")
    print(f"\n{load_info}")
    
    # Run dbt transformations programmatically
    print("\n🚀 Running dbt transformations programmatically...")
    try:
        # Point to the dbt project folder
        dbt_project_path = os.path.join(os.path.dirname(__file__), "dbt_project")
        
        # Initialize the dbt package runner
        # Note: dlt automatically passes the pipeline's MotherDuck credentials to dbt
        dbt = dlt.dbt.package(pipeline, dbt_project_path)
        
        # Run the transformations
        print("🔨 Building staging and marts models...")
        run_info = dbt.run()
        
        # Print results
        print("\n✅ dbt transformations completed successfully!")
        for model in run_info:
            print(f"  - Model: {model.model_name:<15} | Status: {model.status:<10} | Time: {model.time:.2f}s")
            
        # Run dbt tests programmatically
        print("\n🧪 Running dbt tests...")
        test_info = dbt.test()
        print("✅ dbt tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running dbt transformations: {e}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. ✅ Ingestion & dbt transformations completed on MotherDuck!

2. Connect to Lightdash:
   - Database: retail_analytics
   - Schema: transformed
   - Adapter: DuckDB / MotherDuck
   - Auth: MOTHERDUCK_TOKEN env var

3. Build live dashboards in Lightdash:
   - Revenue by Month
   - Orders by Status
   - Revenue by Product Category
   - Top Countries by Revenue
   - Avg Order Value over Time
""")
    print("="*80 + "\n")


def run_pipeline():
    load_sample_shop()


if __name__ == "__main__":
    load_sample_shop()
