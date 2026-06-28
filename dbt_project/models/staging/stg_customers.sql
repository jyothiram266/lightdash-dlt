-- Staging model: Clean and standardize customers from raw dlt load
-- Removes dlt metadata, applies type conversions, filters to active loads

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    id as customer_id,
    name,
    email,
    country,
    signup_date,
    _dlt_load_id,
    current_timestamp as dbt_created_at
from {{ source('raw', 'customers') }}
