#drop database bpstation;
create database if not exists bpstation;
use bpstation;

create table if not exists department(
department_id varchar(30),
department_name varchar(50),
email varchar(100),
phone_number varchar(12),
PRIMARY KEY (department_id)
);

create table if not exists employee(
employee_id varchar(30),
citizen_id varchar(10),
department_id varchar(30),
first_name varchar(50),
last_name varchar(50),
starting_date date,
gender varchar(30),
birth_date date,
email varchar(100),
phone_number varchar(12),
address varchar(100),
PRIMARY KEY (employee_id),
CONSTRAINT fk_department_id FOREIGN KEY (department_id) REFERENCES department(department_id)
);

create table if not exists cases(
case_id varchar(30),
date_occured date,
case_description varchar(1000),
location varchar(100),
case_status varchar(10),
PRIMARY KEY (case_id)
);

create table if not exists investigation(
employee_id varchar(30),
case_id varchar(10),
start_date date,
CONSTRAINT fk_investigation_employee_id FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
CONSTRAINT fk_investigation_case_id FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

create table if not exists report(
report_id int,
reported_to varchar(30),
opened_case varchar(30),
reporter_name varchar(100),
report_date date,
reporter_citizen_id varchar(20),
reporter_phone varchar(12),
PRIMARY KEY (report_id),
CONSTRAINT fk_report_reported_to FOREIGN KEY (reported_to) REFERENCES employee(employee_id),
CONSTRAINT fk_report_opened_case FOREIGN KEY (opened_case) REFERENCES cases(case_id)
);

create table if not exists suspect(
citizen_id varchar(30),
suspect_name varchar(100),
gender varchar(30),
birth_date date,
adress varchar(100),
phone_number varchar(30),
PRIMARY KEY (citizen_id)
);


create table if not exists committed_crime(
case_id varchar(30),
citizen_id varchar(30),
FOREIGN KEY (case_id) REFERENCES cases(case_id),
FOREIGN KEY (citizen_id) REFERENCES suspect(citizen_id)
);