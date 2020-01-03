# Setup instructions

## Configuring SSL
Because Beiwe often deals with sensitive data covered under HIPAA, it's important to add an SSL certificate so that web traffic is encrypted with HTTPS.

The setup script [uses AWS Certificate Manager to generate an SSL certificate](http://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request.html).  AWS Certificate Manager [will check that you control the domain by sending verification emails](http://docs.aws.amazon.com/acm/latest/userguide/gs-acm-validate.html) to the email addresses in the domain's WHOIS listing.


***

# Configuration settings

All the settings listed here can be found either in the constants file or in the
config/settings.py file, or can have an environment variable set for them.

Optional Settings
if an environment variable is provided for any of these they will override the default
value.  More information is available in the constants and config/settings.py files in the
config directory.

```
    DEFAULT_S3_RETRIES - the number of retries on attempts to connect to AWS S3
        default: 1
    CONCURRENT_NETWORK_OPS - the number of concurrent network operations throughout the codebase
        default: 10
    FILE_PROCESS_PAGE_SIZE - the number of files pulled in for processing at a time
        default: 250
    ASYMMETRIC_KEY_LENGTH - length of key files used in the app
        default: 2048
    ITERATIONS - PBKDF2 iteration count for passwords
        default: 1000
```

Mandatory Settings
If any of these are not provided, Beiwe will not run, empty and None values are
considered invalid  Additional documentation can be found in config/setting.pys.

```
    FLASK_SECRET_KEY - a unique, cryptographically secure string
    AWS_ACCESS_KEY_ID - AWS access key for S3
    AWS_SECRET_ACCESS_KEY - AWS secret key for S3
    S3_BUCKET - the bucket for storing app-generated data
    E500_EMAIL_ADDRESS - the source email address for 500 error alerts
    OTHER_EMAIL_ADDRESS - the source email address for other error events
    SYSADMIN_EMAILS - a comma separated list of email addresses for recipients of error reports. (whitespace before and after addresses will be ignored)
    RDS_DB_NAME - postgress database name (the name of the database inside of postgres)
    RDS_USERNAME - database username
    RDS_PASSWORD - database password
    RDS_HOSTNAME - database IP address or url
    S3_ACCESS_CREDENTIALS_USER - the user id for s3 access for your deployment
    S3_ACCESS_CREDENTIALS_KEY - the secret key for s3 access for your deployment
```
