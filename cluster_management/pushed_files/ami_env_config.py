import os
os.environ['SENTRY_ANDROID_DSN'] = 'https://foo:foo@sentry.io/foo'
os.environ['SENTRY_ELASTIC_BEANSTALK_DSN'] = 'https://foo:foo@sentry.io/foo'
os.environ['SENTRY_DATA_PROCESSING_DSN'] = 'https://foo:foo@sentry.io/foo'
os.environ['FLASK_SECRET_KEY'] = 'replace_with_random_string'
os.environ['SENTRY_JAVASCRIPT_DSN'] = 'https://foo@sentry.io/foo'
os.environ['SYSADMIN_EMAILS'] = 'webmaster@localhost'
os.environ['DOMAIN_NAME'] = 'beiwe-dev.ut-wcwh.org'
os.environ['RDS_PASSWORD'] = 'password'
os.environ['RDS_USERNAME'] = 'beiweuser'
os.environ['RDS_DB_NAME'] = 'beiweproject'
os.environ['RDS_HOSTNAME'] = 'localhost'
os.environ['S3_BUCKET'] = 's3_bucket_name'
os.environ['BEIWE_SERVER_AWS_SECRET_ACCESS_KEY'] = 'somestring'
os.environ['BEIWE_SERVER_AWS_ACCESS_KEY_ID'] = 'somestring'
