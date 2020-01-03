import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from config.constants import SYSTEM_EMAIL_ADDRESS

from datetime import datetime

def send_ses_email(destination_address, subject, body, attachment=None):

    email_charset = "UTF-8"

    ses_client = boto3.client('ses', region_name = 'us-east-1')

    message = MIMEMultipart('mixed')

    message['Subject'] = subject
    message['From'] = SYSTEM_EMAIL_ADDRESS
    message['To'] =  destination_address

    # Create a multipart/alternative child container.
    message_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(body.encode(email_charset), 'plain', email_charset)

    message_body.attach(textpart)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    message.attach(message_body)


    if attachment:

        if not isinstance(attachment, dict) or \
            'data' not in attachment or not attachment['data'] or \
            'name' not in attachment or not attachment['name']:
            raise ValueError('Attachment should be a dict containing "data" and "name" keys,'
                             ' each of which should correspond to non-empty values')

        # Define the attachment part and encode it using MIMEApplication.
        message_attachment = MIMEApplication(attachment['data'])

        # Add a header to tell the email client to treat this part as an attachment,
        # and to give the attachment a name.
        message_attachment.add_header('Content-Disposition','attachment',filename=attachment['name'])

        # Add the attachment to the parent container.
        message.attach(message_attachment)

    try:
        #Provide the contents of the email.
        response = ses_client.send_raw_email(
            Source=SYSTEM_EMAIL_ADDRESS,
            Destinations=[
                destination_address
            ],
            RawMessage={
                'Data':message.as_string(),
            },
            #ConfigurationSetName=CONFIGURATION_SET
        )

    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

if __name__ == "__main__":
    send_ses_email('cameron.craddock@gmail.com', 'this is a test', 'this is a test')
    send_ses_email('cameron.craddock@gmail.com', 'this is a test with attachment', 'this is a test',
        attachment={'data':'this is file contents', 'name':'attachment.txt'})


