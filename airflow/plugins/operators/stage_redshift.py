from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    copy_statement = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'   
        format as JSON '{}'
        
    """

    @apply_defaults
    def __init__(self,
                 aws_credentials_id="",
                 conn_id="",
                 table="",
                 s3_bucket="",
                 s3_key="",
                 json_path="",
                 *args, **kwargs):
        
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)

        self.aws_credentials_id = aws_credentials_id
        self.redshift_conn_id = conn_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.json_path = json_path

    def execute(self, context):
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Copying data from S3 to Redshift")

        s3_path = f"s3://{self.s3_bucket}/{self.s3_key}"
        
        run_redshift = StageToRedshiftOperator.copy_statement.format(self.table, s3_path, credentials.access_key,
                                                            credentials.secret_key, self.json_path)
        redshift.run(run_redshift)