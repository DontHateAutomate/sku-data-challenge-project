-- models/gdp_analysis.sql
{{ config(materialized='table') }}

WITH source_data AS (
    -- Step 1: Select and filter the raw data.
    -- We directly reference the table loaded by our Python script.
    -- We also filter for years since 2000 and remove records with no GDP value.
    SELECT
        country_name,
        year,
        gdp_usd
    FROM
        gdp_data.public.raw_gdp_data
    WHERE
        gdp_usd IS NOT NULL AND year >= 2000
),

gdp_with_previous_year AS (
    -- Step 2: Use the LAG window function to get the previous year's GDP.
    -- We need this to calculate the growth rate.
    -- PARTITION BY country_name ensures the calculation restarts for each country.
    SELECT
        country_name,
        year,
        gdp_usd,
        LAG(gdp_usd, 1) OVER (PARTITION BY country_name ORDER BY year) AS previous_year_gdp
    FROM
        source_data
),

gdp_growth_calc AS (
    -- Step 3: Calculate the year-over-year GDP growth percentage.
    SELECT
        country_name,
        year,
        gdp_usd AS gdp,
        -- Use a CASE statement to avoid division-by-zero errors.
        CASE
            WHEN previous_year_gdp IS NULL OR previous_year_gdp = 0 THEN NULL
            ELSE (gdp_usd - previous_year_gdp) / previous_year_gdp
        END AS gdp_growth
    FROM
        gdp_with_previous_year
),

final_model AS (
    -- Step 4: Calculate the running min and max growth since 2000.
    -- The window frame (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) ensures
    -- we only consider years from 2000 up to the current year for each row.
    SELECT
        country_name AS country,
        year,
        gdp,
        gdp_growth,
        MIN(gdp_growth) OVER (PARTITION BY country_name ORDER BY year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS min_gdp_growth_since_2000,
        MAX(gdp_growth) OVER (PARTITION BY country_name ORDER BY year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS max_gdp_growth_since_2000
    FROM
        gdp_growth_calc
)

SELECT * FROM final_model