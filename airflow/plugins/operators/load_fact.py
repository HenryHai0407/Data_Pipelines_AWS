from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'
    sql_query = """
        BEGIN;
        {};
        INSERT INTO {}
        {};
        COMMIT;
    """

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 conn_id = "",
                 table = "",
                 sql_statement = "",
                 append = False,
                 **kwargs):

        super(LoadFactOperator, self).__init__( **kwargs)
        # Map params here
        # Example:
        self.conn_id = conn_id
        self.table = table
        self.sql_statement = sql_statement
        self.append = append

    def execute(self, context):
        self.log.info('Connecting to Postgres')
        redshift = PostgresHook(postgres_conn_id = self.conn_id)
        sql = ""
        if self.append:
            sql = LoadFactOperator.sql_query.format("",self.table, self.sql_statement)   
        else:
            sql = LoadFactOperator.sql_query.format(f"TRUNCATE TABLE {self.table} ", self.table, self.sql_statement)
            
        self.log.info(f"Preparing sql querry {sql }")
        self.log.info(f"loading fact table {self.table}")
        
        redshift.run(sql)