from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 conn_id="",
                 table="",
                 sql_statement="",
                 append=False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)

        self.conn_id = conn_id
        self.table = table
        self.sql_statement= sql_statement
        self.append = append

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.conn_id)
        self.log.info(f"Loading dimension table {self.table}")
        sql = ""

        if self.append:
            sql = """
                    BEGIN;
                    INSERT INTO {}
                    {};
                    COMMIT;""".format(self.table, self.sql_statement)
        else:
            sql = """
                    BEGIN;
                    TRUNCATE TABLE {}; 
                    INSERT INTO {}
                    {}; 
                    COMMIT;""".format(self.table, self.table, self.sql_statement)

        redshift.run(sql)