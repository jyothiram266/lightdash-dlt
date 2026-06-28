-- Dimension model: Customer dimension
-- One row per unique customer with all customer attributes
-- Used for drill-down analysis in Lightdash

{{ config(
    materialized='table',
    schema='transformed'
) }}

select
    customer_id,
    name as customer_name,
    email,
    country,
    signup_date,
    dbt_created_at
from {{ ref('stg_customers') }}
