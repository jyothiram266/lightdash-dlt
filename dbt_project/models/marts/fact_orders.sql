-- Fact model: Orders
-- Core fact table for BI layer
-- One row per order with all order metrics and dimensional attributes
-- Revenue = quantity * product price (business logic)
-- This is the primary table for Lightdash metrics and explores

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    o.order_id,
    o.customer_id,
    o.product_id,
    o.quantity,
    o.order_date,
    o.status,
    c.customer_name,
    c.country as customer_country,
    c.email as customer_email,
    c.signup_date,
    p.product_name,
    p.category as product_category,
    p.price as product_price,
    -- Calculate revenue (business logic: quantity * price)
    (o.quantity * p.price) as revenue,
    o.dbt_created_at,
    current_timestamp as dbt_updated_at
from {{ ref('stg_orders') }} o
left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
left join {{ ref('dim_products') }} p on o.product_id = p.product_id
