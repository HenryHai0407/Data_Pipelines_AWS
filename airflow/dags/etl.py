from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator, CreateTableOperator)
from helpers import SqlQueries
from create_tables_queries import sql

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'Hai Nguyen',
    'start_date': datetime.now(),
    'retries': 3,
    'retry_delay': timedelta(seconds=15),
    'email_on_retry': False,
    'depends_on_past': True,
    'max_active_runs' : 1
}

dag = DAG('udac_example_dag',
          start_date = datetime.now(),
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)



create_tables_on_redshift = CreateTableOperator(
    task_id = 'create_tables',
    conn_id = 'redshift',
    sql_statement = sql,
    dag = dag
)


stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    conn_id = "redshift",
    aws_credentials_id = "aws_credentials",
    table = "staging_events",
    s3_bucket = "udacity-dend",
    s3_key = "log_data",
    json_path = "s3://udacity-dend/log_json_path.json",
    dag=dag
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    conn_id = "redshift",
    aws_credentials_id = "aws_credentials",
    table = "staging_songs",
    s3_bucket = "udacity-dend",
    s3_key = "song_data/A/A/A",
    json_path = "auto",
    dag=dag
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    conn_id = "redshift",
    table = "songplays",
    sql_statement = SqlQueries.songplay_table_insert,
    append = False,
    dag=dag
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    conn_id = "redshift",
    table = "users",
    sql_statement = SqlQueries.user_table_insert,
    append = False,
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    conn_id = "redshift",
    table = "songs",
    sql_statement = SqlQueries.song_table_insert,
    append = False,
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    conn_id = "redshift",
    table = "artists",
    sql_statement = SqlQueries.artist_table_insert,
    append = False,
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    conn_id = "redshift",
    table = "time",
    sql_statement = SqlQueries.time_table_insert,
    append = False,
    dag=dag
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    conn_id = 'redshift',
    tables = ['songplays', 'users', 'songs', 'artists', 'time'],
    dag=dag
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)



start_operator >> create_tables_on_redshift

create_tables_on_redshift >> stage_songs_to_redshift
create_tables_on_redshift >> stage_events_to_redshift

stage_songs_to_redshift >> load_songplays_table
stage_events_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator