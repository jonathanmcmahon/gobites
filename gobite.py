import os
import random

import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# go1.11
URL_BASE = "https://github.com/golang/go/tree/41e62b8c49d21659b48a95216e3062032285250f/src/"


def send_email(name, url):

    SENDER = os.getenv("SENDER")

    RECIPIENT = os.getenv("RECIPIENT")

    AWS_REGION = os.getenv("AWS_REGION")

    SUBJECT = "golang/go source: %s" % name

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Here's your daily dose of golang source code: \r\n%s\r\n\r\n--The Gopher Factory" % name

    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <p>Here's your daily dose of golang source code:</p>
    <p><h3><b><a href="{0}">{1}</a></b></h3></p>
    <p>&nbsp;</p>
    <p><i>&mdash;The Gopher Factory</p>
    </body>
    </html>
    """

    BODY_HTML = BODY_HTML.format(url, name)

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
            # ConfigurationSetName=CONFIGURATION_SET
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['ResponseMetadata']['RequestId'])


def pick_srcfile():

    with open("suffix.txt") as f:
        src_files = f.readlines()

    src_files= [x for x in src_files]
    print("Number of files: %d" % len(src_files))
    key = random.choice(src_files)
    print("Randomly selected file:\n%s" % key)

    url = URL_BASE + key
    return key, url


def gobite(event, context):
    key, url = pick_srcfile()
    send_email(key, url)
    return "Email sent!"


if __name__ == "__main__":
    gobite("","")
