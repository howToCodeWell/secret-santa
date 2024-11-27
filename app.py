import random
import smtplib
import ssl
import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MODE = os.environ.get("MODE", "dev")
SEND_EMAIL = os.getenv("SEND_EMAIL", 'False').lower() in ('true', '1', 't')

def file_checks():
    if os.path.exists('.env') is False:
        print('.env file is missing')
        exit(1)
    if os.path.exists('users.json') is False:
        print('users.json file is missing')
        exit(1)
    if os.path.exists('email_template.txt') is False:
        print('email_template.txt file is missing')
        exit(1)

def get_users():
    with open("./users.json") as json_file:
        json_data = json.load(json_file)
    return json_data['users']


def make_subject():
    now = datetime.datetime.now()
    email_subject_prefix = os.environ.get("EMAIL_SUBJECT_PREFIX")
    return email_subject_prefix + " " + str(now.year)


def read_template(filename):
    with open(filename, 'r') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def send_messages(results):
    print("Setting up messages")
    subject = make_subject()
    message_template = read_template('email_template.txt')

    email_from_address = os.environ.get("FROM_ADDRESS")
    smtp_address = os.environ.get("SMTP_ADDRESS")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")

    context = ssl.create_default_context()
    # set up the SMTP server
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.ehlo()
    server.starttls(context=context)
    server.login(smtp_address, smtp_password)

    while len(results) > 0:
        result = results.pop()

        name = result.get('name')
        email = result.get('email')
        receiver = result.get('receiver')

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name,
                                              GIVING_TO=receiver,
                                              SUBJECT=subject,
                                              FROM_ADDRESS=email_from_address)

        if "dev" in MODE:
            print(message)

        if SEND_EMAIL:
            print('Sending email to ' + email)
            # send the message via the server set up earlier.
            server.sendmail("NO-REPLY@SANTA-LAND.faraway", email, message)

    # Terminate the SMTP session and close the connection
    server.quit()


def generate_matches(users):
    assigned = []
    if len(users) < 2:
        raise Exception("Sorry, at least two users are needed. Found " + str(len(users)))

    if len(users) % 2 != 0:
        raise Exception("Sorry, there must be an even number of users. Found " + str(len(users)))

    first_person = ''
    person2 = ''
    while len(users) > 0:
        # Set name 1 to the first element of the list and remove
        person1 = users.pop()

        # Set the first name if it hasn't been set already
        if not first_person:
            first_person = person1

        # Print name 2 and 1 if known
        if person2 and person1:
            assigned.append({
                'name': person2.get('name'),
                'email': person2.get('email'),
                'receiver': person1.get('name')
            })

        # Make sure we have another element.
        # This ensures we can have odd and even elements
        if len(users) > 0:
            # Remove the next name and set to name2
            person2 = users.pop()

            assigned.append({
                'name': person1.get('name'),
                'email': person1.get('email'),
                'receiver': person2.get('name')
            })
        else:
            # We don't have name 2 so set it to name 1
            person2 = person1

    assigned.append({
        'name': person2.get('name'),
        'email': person2.get('email'),
        'receiver': first_person.get('name')
    })

    return assigned


def print_debug(matches):
    print("\nPrinting debug\n")
    for match in matches:
        print(match.get('name') + ' buys for ' + match.get('receiver'))


def main():
    print("Welcome to Secret Santa")
    print("Running in " + MODE + " mode")

    file_checks()

    users = get_users()
    print("Found " + str(len(users)) + " users")

    print("Shuffling users")
    random.shuffle(users)

    assigned = generate_matches(users)
    print(str(len(assigned)) + " matches made")

    if "dev" in MODE:
        print(assigned)
        print_debug(assigned)

    if len(assigned) >= 2 and SEND_EMAIL:
        send_messages(assigned)


if __name__ == '__main__':
    main()
