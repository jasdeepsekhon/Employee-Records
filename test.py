from jinja2 import Environment, FileSystemLoader
from jinja2 import Environment
import oracledb
from flask import Flask, redirect, request
from datetime import datetime


un = ""
pw = ""
cs = "enter db oracle"

# Define folder for Jinja to look for html templates
file_loader = FileSystemLoader('templates')
# Initialize Jinja Enviroment
env = Environment(loader=file_loader)

# Connect to OracleDB
connection = oracledb.connect(user=un, password=pw, dsn=cs)
# Open cursor on connection
cursor = connection.cursor()

# Define flask App
# We also set the path for static files (root) and which folder to look for static files in
app = Flask(__name__, static_url_path='', static_folder='static')


@app.route("/employee/hiring_form", methods=['GET', 'POST'])
def hiring_form():
    # Load template
    hiring_form_template = env.get_template('hiring_form.html')
    # Select all jobs and convert into a list
    jobs = list(cursor.execute("select * from HR_JOBS"))
    # Select all departments and convert into a list
    departments = list(cursor.execute(
        "select department_id, department_name from HR_DEPARTMENTS"))
    # Select all unique manager_id and merge on the same table getting first_name and last_name
    managers = list(cursor.execute(
        "SELECT unique(e.manager_id), m.first_name, m.last_name FROM HR_EMPLOYEES e JOIN HR_EMPLOYEES m on (e.manager_id = m.employee_id) ORDER BY e.manager_id"))
    # Select all departments and convert into a list
    email = request.form.get("Email")
    error_msg = None
    if email is not None:
        print(request.form)
        phone_number = request.form.get("Phone")
        salary = float(request.form.get("Salary"))
        first_name = request.form.get("First_name")
        last_name = request.form.get("Last_name")
        hire_date = request.form.get("Hire_date")
        manager_id = request.form.get("Manager_ID")
        department_id = request.form.get("Department_ID")
        job_id = request.form.get("Job")
        # Format date object into string
        datetime_object = datetime.strptime(hire_date, '%Y-%m-%d')

        # Call procedure "employee_hire_sp" with the new values from the form
        try:
            cursor.callproc('employee_hire_sp', [first_name, last_name, email, salary,
                            datetime_object, phone_number, job_id, manager_id, department_id])

        except oracledb.DatabaseError as e:
            error_obj, = e.args
            print(error_obj)
            if error_obj.code == 20100:
                error_msg = "Invalid Salary"

    return hiring_form_template.render(jobs=jobs, departments=departments, managers=managers, error_msg=error_msg)


@app.route("/employee/records", methods=['GET', 'POST'])
def records():
    # Load template
    records_template = env.get_template('records.html')
    email = request.form.get("email")
    error_msg = None
    if email is not None:
        # Select all departments and convert into a list
        employee_id = int(request.form.get("employee_id"))

        phone_number = request.form.get("phone_number")
        salary = float(request.form.get("salary"))

        try:
            cursor.callproc('updating_employee', [
                employee_id, email, salary, phone_number])
        except oracledb.DatabaseError as e:
            print("error")
            error_obj, = e.args
            if error_obj.code == 20100:
                error_msg = "Invalid Salary"
    # Call procedure "updating_employee" with the new values from the form
    connection.commit()

    # Query all employees ordering my employee_id
    records = list(cursor.execute(
        "select * from HR_EMPLOYEES ORDER BY employee_id"))

    return records_template.render(records=records, error_msg=error_msg)


@app.route("/jobs/jobdesc")
def jobs_desc():
    # Load template
    jobs_desc_template = env.get_template('jobdesc.html')

    job_id = request.args.get("job_id")

    # Select all jobs and convert into a list
    jobs = list(cursor.execute("select * from HR_JOBS"))

    job_desc = None
    if job_id is not None:
        for job in jobs:
            if job[0] == job_id:
                job_desc = job
    return jobs_desc_template.render(jobs=jobs, job_desc=job_desc)


@app.route("/jobs/updatejob", methods=['GET', 'POST'])
def jobs_update():
    # Load template
    jobs_update_template = env.get_template('updatejob.html')
    job_id = request.form.get("job_id")
    job_title = request.form.get("job_title")
    job_min_salary = request.form.get("min_salary")
    job_max_salary = request.form.get("max_salary")
    if job_id is not None:
        cursor.execute(
            f"UPDATE HR_JOBS SET job_title='{job_title}', min_salary={job_min_salary}, max_salary={job_max_salary} WHERE job_id='{job_id}'")
        connection.commit()

    # Select all jobs and convert into a list
    jobs = list(cursor.execute("select * from HR_JOBS ORDER BY job_id"))

    return jobs_update_template.render(jobs=jobs)


@app.route("/jobs/createjob", methods=['GET', 'POST'])
def jobs_create():

    # Load template
    hiring_createjob_template = env.get_template('createjob.html')

    # Select all departments and convert into a list
    job_id = request.form.get("job_id")
    job_title = request.form.get("job_title")
    job_min_salary = request.form.get("min_salary")
    if job_id is not None:
        # Call procedure "create_job" with the new values from the form
        cursor.callproc(
            'new_job', [job_id, job_title, job_min_salary])

    return hiring_createjob_template.render()
