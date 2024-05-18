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

    # generate department data
    # field officers, administrative workers and investigators.

    for department_type in ["field_officer", "administrative", "investigator"]:
        d = {}
        d['department_id'] = fake.unique.uuid4()[:8]
        d['email'] = department_type + "@erasmusmail.com"
        d['phone_number'] = fake.phone_number()
        data['department'].append(d)
        
    # EMPLOYEE
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

    # CASES
    for i in range(100):
        c = {}
        c['case_id'] = (fake.case_type() + fake.unique.uuid4())[:8]
        c['date_occurred'] = fake.date_time_between(start_date='-3y', end_date=date.today())
        c['case_description'] = fake.sentence(nb_words=10)
        c['location'] = fake.address()
        c['case_status'] = fake.case_status()
        data['cases'].append(c)

    # SUSPECT
    for i in range(50):
        s = {}
        s['citizen_id'] = fake.unique.ssn()
        s['suspect_name'] = fake.name()
        s['gender'] = random.choice(['Male', 'Female'])
        s['birth_date'] = fake.date_of_birth()
        s['address'] = fake.address()
        s['phone_number'] = fake.phone_number()
        data['suspect'].append(s)

    # COMMITED CRIME
    for case in data['cases']:
        c = {}
        c['case_id'] = case['case_id']
        c['citizen_id'] = random.choice(data['suspect'])['citizen_id']
        data['committed_crime'].append(c)

    # REPORT
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

def write_csv(directory, data):
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for table_name, rows in data.items():
        # Construct the file path
        file_path = os.path.join(directory, f"{table_name}.csv")
        
        # Write the table to a CSV file
        with open(file_path, 'w', newline='') as csvfile:
            if rows:  # Only write if there are rows
                writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        

def read_csv(directory):
    data = {}

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            
            # Read the CSV file
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                data[filename[:-4]] = [row for row in reader]
    
    return data

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

# insert data to database
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
    
    # input validation
    if (len(argv) != 3 and len(argv) != 2) or (argv[1] != 'generate' and argv[1] != 'populate' ):
        print('Usage: populator.py [generate | populate, csvpath]')
        exit()
    if len(argv) == 2 :
        directory = os.path.join(os.getcwd(), 'dummydata')
    else: 
        directory = os.path.join(os.getcwd(), argv[2])
    
    # GENERATE
    if argv[1] == 'generate':
        
        # check if already generated files
        if os.path.exists(directory) and os.path.isfile(os.path.join(directory, 'employee.csv')):    
            print('There exists .csv files on the given path.')
            ans = input('This operation will override the existing files.\
                Do you want to continue? (y/n): ')
            if ans != 'y':
                exit()

        fake_data = generate_fake_data()
        
        write_csv(directory, fake_data)

    # POPULATE
    elif argv[1] == 'populate':
        
        conn = connect_to_database()
        cursor = conn.cursor()
        
        fake_data = read_csv(directory)
        
        for table_name, data in fake_data.items():
            insert_data(conn, cursor, table_name, data)

        cursor.close()
        conn.close()
    

    


