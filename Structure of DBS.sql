CREATE DATABASE tariff;
CREATE TABLE tariff_impact (
country VARCHAR(60),
product_name VARCHAR(120),
product_type VARCHAR(60),
price_before_USD DECIMAL(10,2),
price_after_USD DECIMAL (10,2),
tariff_pct DECIMAL (5,2),
increase_date VARCHAR(10),
Units_sold_Before INT,
Units_sold_after INT);

BULK INSERT tariff_impact
FROM 'D:\Project\Tariff Impact Analysis\Tariff Impact Analysis.csv'
WITH (
    FIRSTROW = 2,            -- Skip the header row
    FIELDTERMINATOR = ',',   -- Comma as field delimiter
    ROWTERMINATOR = '\n',    -- New line as row delimiter
    TABLOCK
);

-- Hypothesis 1: Tariffs increased the average product prices
SELECT 
    product_name,
    AVG(price_before_USD) AS avg_price_before_USD,
    AVG(price_after_USD) AS avg_price_after_USD,
    AVG(price_after_USD - price_before_USD) AS avg_price_increase
FROM tariff_impact
GROUP BY product_name
ORDER BY avg_price_increase DESC;

-- Hypothesis 2: Unit sales decreased after tariffs

SELECT
    product_name,
    SUM(units_sold_before) AS total_units_before,
    SUM(units_sold_after) AS total_units_after,
    SUM(units_sold_after) - SUM(units_sold_before) AS units_difference
FROM tariff_impact
GROUP BY product_name
ORDER BY units_difference ASC;

-- Hypothesis 3: Tariff impact varies by country

SELECT
    country,
    SUM(units_sold_before) AS total_units_before,
    SUM(units_sold_after) AS total_units_after,
    SUM(units_sold_after) - SUM(units_sold_before) AS units_difference
FROM tariff_impact
GROUP BY country
ORDER BY units_difference ASC;

-- Hypothesis 4: Electronics products suffered the highest percentage price increase

SELECT
    product_type,
    AVG(price_before_USD) AS avg_price_before_USD,
    AVG(price_after_USD) AS avg_price_after_USD,
    AVG(CAST(price_after_USD - price_before_USD AS FLOAT) / price_before_USD * 100) AS avg_price_pct_increase
FROM tariff_impact
WHERE product_type = 'Electronics'
GROUP BY product_type;

-- Hypothesis 5: Products with higher tariff percentages saw greater sales decreases

SELECT
    product_name,
    AVG(tariff_pct) AS avg_tariff_pct,
    SUM(units_sold_before) AS total_units_before,
    SUM(units_sold_after) AS total_units_after,
    SUM(units_sold_after) - SUM(units_sold_before) AS units_difference
FROM tariff_impact
GROUP BY product_name
ORDER BY avg_tariff_pct DESC, units_difference ASC;

-- Hypothesis 6: Specific products with sharp sales declines

SELECT TOP 10
    product_name,
    SUM(units_sold_before) AS total_units_before,
    SUM(units_sold_after) AS total_units_after,
    SUM(units_sold_after) - SUM(units_sold_before) AS units_difference
FROM tariff_impact
GROUP BY product_name
ORDER BY units_difference ASC;

-- Hypothesis 7: Percent change in sales to classify impact

SELECT
    product_name,
    SUM(units_sold_before) AS total_units_before,
    SUM(units_sold_after) AS total_units_after,
    CASE 
        WHEN SUM(units_sold_before) = 0 THEN NULL
        ELSE CAST((SUM(units_sold_after) - SUM(units_sold_before)) AS FLOAT) / SUM(units_sold_before) * 100
    END AS pct_change_units_sold
FROM tariff_impact
GROUP BY product_name
ORDER BY pct_change_units_sold ASC;

SELECT * 
FROM fn_my_permissions('dbo.tariff_impact', 'OBJECT');











