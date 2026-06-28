-- Dimension model: Product dimension
-- One row per unique product with all product attributes
-- Used for filtering and drill-down in Lightdash

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    product_id,
    name as product_name,
    category,
    price,
    created_date,
    dbt_created_at
from {{ ref('stg_products') }}
