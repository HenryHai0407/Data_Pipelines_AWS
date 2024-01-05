from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from create_tables_queries import sql

class CreateTableOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 conn_id = "",
                 tables = [],
                 sql_statement = "",
                 *args, **kwargs):

        super(CreateTableOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        self.conn_id = conn_id
        self.tables = tables
        self.sql = sql_statement

    def execute(self, context):
        redshift = PostgresHook(self.conn_id)
        
        redshift.run(sql)