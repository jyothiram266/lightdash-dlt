-- Staging model: Clean and standardize orders from raw dlt load
-- Removes dlt metadata, applies type conversions, filters to active loads
-- Prepares for dimensional join in marts layer

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    id as order_id,
    customer_id,
    product_id,
    quantity,
    order_date,
    status,
    _dlt_load_id,
    current_timestamp as dbt_created_at
from {{ source('raw', 'orders') }}
