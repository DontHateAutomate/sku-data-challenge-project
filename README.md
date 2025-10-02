This project tackles a three-part data challenge, covering raw data engineering to analytics and final visualization. 
I started by building a Python script to pull global GDP data from the World Bank's API, loading it into a local PostgreSQL database managed with Docker. 
From there, I used dbt to transform and model the raw data, calculating key required metrics like year-over-year growth and running tests to ensure data quality. 
The final piece is a dashboard built in Looker Studio that visualizes retail sales data, providing a clear, interactive view of operational insights like top-performing products and sales trends.

## How to Run the Project

This guide provides step-by-step instructions to reproduce the project, from setting up the database to running the data transformations.

### Prerequisites

* Docker Desktop installed and running.
* Python 3.9 or higher installed.

### Part 1: Data Engineering (Ingestion)

This part will set up the local PostgreSQL database and ingest the GDP data from the World Bank API.

1.  **Start the Database**:
    Open a terminal in the project's root directory (`Sku_Challenge/`) and run:
    ```bash
    docker compose up -d
    ```

2.  **Set up Python Environment**:
    Create and activate a virtual environment:
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create Environment File**:
    In the root directory, create a file named `.env` and add the following content:
    ```
    DB_NAME="gdp_data"
    DB_USER="user"
    DB_PASSWORD="password"
    DB_HOST="localhost"
    DB_PORT="5432"
    ```

5.  **Run the Ingestion Script**:
    Execute the Python script to fetch the API data and load it into your Dockerized database:
    ```bash
    python ingestion_script.py
    ```
    At the end of this step, the `raw_gdp_data` table will be populated in your PostgreSQL database.

### Part 2: Analytics Engineering (Transformation)

This part will use dbt to transform the raw data into the final `gdp_analysis` table.

1.  **Configure dbt Profile**:
    Navigate to your user's dbt directory (usually `C:/Users/YourUser/.dbt/`) and create a file named `profiles.yml`. Add the following configuration:
    ```yaml
    gdp_dbt_project:
      target: dev
      outputs:
        dev:
          type: postgres
          host: localhost
          user: user
          password: password
          port: 5432
          dbname: gdp_data
          schema: public
          threads: 4
    ```

2.  **Install dbt Packages**:
    Navigate into the dbt project folder and install the necessary packages:
    ```bash
    cd gdp_dbt_project
    dbt deps
    ```

3.  **Run dbt Build**:
    Execute the `dbt build` command. This will run your models and execute your tests in a single command.
    ```bash
    dbt build
    ```
    After this step, the `gdp_analysis` table will be created and validated in your database.
