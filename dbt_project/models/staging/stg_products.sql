-- Staging model: Clean and standardize products from raw dlt load
-- Removes dlt metadata, applies type conversions, filters to active loads

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    id as product_id,
    name,
    category,
    price,
    created_date,
    _dlt_load_id,
    current_timestamp as dbt_created_at
from {{ source('raw', 'products') }}
