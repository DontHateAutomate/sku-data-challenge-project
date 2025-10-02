This project tackles a three-part data challenge, covering raw data engineering to analytics and final visualization. 
I started by building a Python script to pull global GDP data from the World Bank's API, loading it into a local PostgreSQL database managed with Docker. 
From there, I used dbt to transform and model the raw data, calculating key required metrics like year-over-year growth and running tests to ensure data quality. 
The final piece is a dashboard built in Looker Studio that visualizes retail sales data, providing a clear, interactive view of operational insights like top-performing products and sales trends.
