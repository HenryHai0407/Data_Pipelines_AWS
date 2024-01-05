# Data Pipelines with Airflow

Welcome to the Data Pipelines with Airflow project! This endeavor will provide you with a solid understanding of Apache Airflow's core concepts. Your task involves creating custom operators to execute essential functions like staging data, populating a data warehouse, and validating data through the pipeline.

To begin, we've equipped you with a project template that streamlines imports and includes four unimplemented operators. These operators need your attention to turn them into functional components of a data pipeline. The template also outlines tasks that must be interconnected for a coherent and logical data flow.

A helper class containing all necessary SQL transformations is at your disposal. While you won't have to write the ETL processes, your responsibility lies in executing them using your custom operators.

## Initiating the Airflow Web Server
Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed before proceeding.

To bring up the entire app stack up, we use [docker-compose](https://docs.docker.com/engine/reference/commandline/compose_up/) as shown below

```bash
docker-compose up -d
```
Visit http://localhost:8080 once all containers are up and running.

## Configuring Connections in the Airflow Web Server UI
![Airflow Web Server UI. Credentials: `airflow`/`airflow`.](assets/login.png)

On the Airflow web server UI, use `airflow` for both username and password.
* Post-login, navigate to **Admin > Connections** to add required connections - specifically, `aws_credentials` and `redshift`.
* Don't forget to start your Redshift cluster via the AWS console.
* After completing these steps, run your DAG to ensure all tasks are successfully executed.

## Getting Started with the Project
1. The project template package comprises three key components:
   * The **DAG template** includes imports and task templates but lacks task dependencies.
   * The **operators** folder with operator templates.
   * A **helper class** for SQL transformations.

1. With these template files, you should see the new DAG in the Airflow UI, with a graph view resembling the screenshot below:
![Project DAG in the Airflow UI](assets/final_project_dag_graph1.png)
You should be able to execute the DAG successfully, but if you check the logs, you will see only `operator not implemented` messages.

# Data source
*  Song data: `s3://udacity-dend/song_data`
*  Log data: `s3://udacity-dend/log_data`
  
## DAG Configuration
In the DAG, add `default parameters` based on these guidelines:
* No dependencies on past runs.
* Tasks are retried three times on failure.
* Retries occur every five minutes.
* Catchup is turned off.
* No email on retry.

Additionally, configure task dependencies to match the flow depicted in the image below:
![Working DAG with correct task dependencies](assets/final_project_dag_graph2.png)

## Operators
Operators create necessary tables, stage the data, transform the data, and run checks on data quality.

Connections and Hooks are configured using Airflow's built-in functionalities.

All of the operators and task run SQL statements against the Redshift database.


### Stage Operators

The stage operator uploads files in JSON and CSV formats from S3 to Amazon Redshift. This operator initiates and executes a SQL COPY statement based on the provided parameters, specifying the S3 location of the file to be loaded and the target table.

In the DAG, there's a task responsible for staging CSV and JSON data using the RedshiftStage operator. This task facilitates the movement of data from S3 to Redshift by executing a Redshift copy statement.

The task is parameterized: Instead of employing a static SQL statement for staging, the task dynamically generates the copy statement using parameters. It incorporates a templated field, enabling it to load timestamped files from S3 based on the execution time and perform backfills.

Logging is integrated: The operator includes logging mechanisms at various stages of the execution process.

Establishing the database connection involves utilizing a hook and a connection: SQL statements are executed through an Airflow hook.

### Fact and Dimension Operators

The dimension and fact operators leverage the SQL helper class for executing data transformations. These operators take the SQL statement from the helper class as input and specify the target database on which to execute the query. Additionally, a target table is defined to store the outcomes of the transformation.

Dimension loads follow the truncate-insert pattern, where the target table is cleared before the load. There is a parameter that enables the switch between insert modes during dimension loading. Since fact tables are extensive, they only support append-type functionality.

The DAG incorporates a set of tasks utilizing the LoadDimension operator for dimension loading, adhering to the truncate-insert pattern.

Similarly, a task employing the LoadFact operator is included in the DAG for loading facts.

Both operators utilize params: Instead of employing a static SQL statement for staging the data, the task dynamically generates the copy statement using parameters.

The dimension task incorporates a param to facilitate the switch between append and insert-delete functionality: The DAG provides the flexibility to toggle between append-only and delete-load functionality.

### Data Quality Operator

The data quality operator serves the purpose of executing checks on the data itself. Its primary function involves receiving one or more SQL-based test cases along with their expected results and executing these tests. For each test, the operator compares the test result with the expected result, and if there is a mismatch, the operator raises an exception. Subsequently, the task is retried, ultimately failing if the issue persists.

As an illustration, a test could involve a SQL statement checking if a specific column contains NULL values by counting all the rows with NULL in that column. Since the aim is to have no NULLs, the expected result would be 0, and the test compares the SQL statement's outcome to this expected result.

The DAG features a task utilizing the data quality operator, ensuring at least one data quality check is performed. This check is conducted using the appropriate operator.

The operator triggers an error if the check fails, leading to either DAG failure or a specified number of retries.

The operator is designed to be parametrized: It uses params to obtain the tests and their expected results, eliminating the need to hard code tests into the operator.



## Project Backbones:

-[Initial Plugins for Airflow](airflow/plugins/__init__.py)

-[Define Columns and Create Tables](airflow/dags/create_tables_queries.py)

-[The whole ETL process: Tasks and Task Dependencies](airflow/dags/etl.py)

-[Intitialize SQL_Queries file](airflow/plugins/helpers/__init__.py)

-[SQL_Queries file](airflow/plugins/helpers/sql_queries.py)

-[Initialize all Operators](airflow/plugins/operators/__init__.py)

-[Create Tables for Operators](airflow/plugins/operators/create_tables.py)

-[Check Data Quality](airflow/plugins/operators/data_quality.py)

-[Load Dimension Tables](airflow/plugins/operators/load_dimension.py)

-[Load Fact Tables](airflow/plugins/operators/load_fact.py)

-[Stage All Tables to RedShift Data Warehouse](airflow/plugins/operators/stage_redshift.py)


