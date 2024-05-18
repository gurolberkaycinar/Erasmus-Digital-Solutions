import sys
import os
import random
import csv
from datetime import date, datetime, timedelta


import mysql.connector
from mysql.connector import errorcode

from faker import Faker
from faker.providers import DynamicProvider

casetype_provider = DynamicProvider(
     provider_name="case_type",
     elements=["robbery", "murder", "other"],
)

casestatus_provider = DynamicProvider(
    provider_name="case_status",
    elements=["ongoing", "solved", "onhold"]
)

fake = Faker()
fake.add_provider(casetype_provider)
fake.add_provider(casestatus_provider)

# Function to generate fake data using Faker library
def generate_fake_data():
    
    data = {
        'employee': [],
        'department': [],
        'cases': [],
        'suspect': [],
        'committed_crime': [],
        'report': [],
        'investigation': []
    }

    # Generate department data
    # field officers, administrative workers and investigators.

    for department_type in ["field_officer", "administrative", "investigator"]:
        d = {}
        d['department_id'] = fake.unique.uuid4()[:8]
        d['email'] = department_type + "@erasmusmail.com"
        d['phone_number'] = fake.phone_number()
        data['department'].append(d)
        
    # Generate employee data
    for i in range(30):
        e = {}
        e['employee_id'] = fake.unique.uuid4()[:8]
        e['citizen_id'] = fake.unique.ssn()
        e['department_id'] = random.choice(data['department'])['department_id']
        e['first_name'] = fake.first_name()
        e['last_name'] = fake.last_name()
        e['starting_date'] = fake.date_between(start_date='-10y', end_date=date.today())
        e['gender'] = random.choice(['Male', 'Female'])
        e['birth_date'] = fake.date_of_birth()
        e['email'] = e['first_name'] + e['last_name'] + "@erasmusmail.com"
        e['phone_number'] = fake.phone_number()
        e['address'] = fake.address()
        data['employee'].append(e)

    # Generate cases data
    for i in range(100):
        c = {}
        c['case_id'] = (fake.case_type() + fake.unique.uuid4())[:8]
        c['date_occurred'] = fake.date_time_between(start_date='-3y', end_date=date.today())
        c['case_description'] = fake.sentence(nb_words=10)
        c['location'] = fake.address()
        c['case_status'] = fake.case_status()
        data['cases'].append(c)

    # Generate suspect data
    for i in range(50):
        s = {}
        s['citizen_id'] = fake.unique.ssn()
        s['suspect_name'] = fake.name()
        s['gender'] = random.choice(['Male', 'Female'])
        s['birth_date'] = fake.date_of_birth()
        s['address'] = fake.address()
        s['phone_number'] = fake.phone_number()
        data['suspect'].append(s)

    # Generate committed crime data
    for case in data['cases']:
        c = {}
        c['case_id'] = case['case_id']
        c['citizen_id'] = random.choice(data['suspect'])['citizen_id']
        data['committed_crime'].append(c)

    # Generate report data
    for i in range(50):
        r = {}
        r['report_id'] = fake.unique.random_number(digits=8)
        r['reported_to'] = random.choice(data['employee'])['employee_id']
        r['opened_case'] = random.choice(data['cases'])['case_id']
        r['reporter_name'] = fake.name()
        r['report_date'] = fake.date_time_this_year()
        r['reporter_citizen_id'] = fake.ssn()
        r['reporter_phone'] = fake.phone_number()
        data['report'].append(r)

    # Generate investigation data
    for report in data['report']:
        i = {}
        i['employee_id'] = report['reported_to']
        i['case_id'] = report['opened_case']
        i['start_date'] = report['report_date']
        data['investigation'].append(i)

    #print(data)
    return data

#def write_csv(filename, data):
#    with open(filename, 'w', newline='') as csvfile:
#        tables = ['employee', 'department', 'cases', 'suspect', 'commited_crime', 'report', 'investigation']
#        for table in tables:
#            for row in data[table]:
#                print(row)
#                writer = csv.DictWriter(csvfile, fieldnames=row.keys())
#                writer.writeheader()
#                for entry in zip(*row.values()):
#                    writer.writerow(dict(zip(row.keys(), entry)))

def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, values in data.items():
            writer.writerow([key])
            if values:  # Check if the list is not empty
                header_written = False
                for entry in values:
                    if not header_written:
                        writer.writerow(entry.keys())  # Write header only once
                        header_written = True
                    writer.writerow(entry.values())
            writer.writerow([])  # Add an empty row between sections

        

def read_csv():
    ('')

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="gurolberkay",
            password="password",
            database="bpstation"
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

# Function to insert data into database
def insert_data(conn, cursor, table_name, data):
    try:
        if table_name == 'department':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s)", data)
        elif table_name == 'employee':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", data)
        elif table_name == 'cases':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s)", data)
        elif table_name == 'suspect':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s, %s)", data)
        elif table_name == 'committed_crime':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s)", data)
        elif table_name == 'report':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        elif table_name == 'investigation':
            cursor.executemany(f"INSERT INTO {table_name} VALUES (%s, %s, %s)", data)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error inserting data into {table_name} table:", err)

if __name__ == "__main__":
    
    argv = sys.argv
    
    # Input validation
    if (len(argv) != 3 and len(argv) != 2) or (argv[1] != 'generate' and argv[1] != 'populate' ):
        print('Invalid input.')
        print('Usage: populator.py [generate | populate, filename]')
        exit()
    if len(argv) == 2 :
        filename = 'fakedata.csv'
    else: 
        filename = argv[2]
    if '.csv' not in filename:
        if '.' in filename:
            print('Usage only supported with .csv files.')
        filename += '.csv'
    
    # Generate data
    if argv[1] == 'generate':
        if os.path.isfile(filename):
            print('The file "' + filename + '" already exists.')
            ans = input('This operation will override the existing file.\
                  Do you want to continue? (y/n): ')
            if ans != 'y':
                exit()
        # Generate data
        fake_data = generate_fake_data()
        # Write data to file
        write_csv(filename, fake_data)

    # Populate database
    elif argv[1] == 'populate':
        # Connect to database
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Read data
        fake_data = read_csv(filename)
        
        # Insert data into tables
        for table_name, data in fake_data.items():
            insert_data(conn, cursor, table_name, data)

        # Close cursor and connection
        cursor.close()
        conn.close()
    

    


