create or replace PROCEDURE employee_hire_sp(
    p_first_name HR_employees.first_name%TYPE,
    p_last_name HR_employees.last_name%TYPE,
    p_email HR_employees.email%TYPE,
    p_salary HR_employees.salary%TYPE,
    p_hire_date HR_employees.hire_date%TYPE,
    p_phone HR_employees.phone_number%TYPE,
    p_job_id HR_employees.job_id%TYPE,
    p_manager_id HR_employees.manager_id%TYPE,
    p_department_id HR_employees.department_id%TYPE
)
IS
BEGIN
	INSERT INTO HR_EMPLOYEES(FIRST_NAME, LAST_NAME, EMAIL, SALARY, HIRE_DATE, 
    PHONE_NUMBER, JOB_ID, MANAGER_ID, DEPARTMENT_ID)
    VALUES(p_first_name, p_last_name, p_email,p_salary,p_hire_date,p_phone,
    p_job_id, p_manager_id,p_department_id);

END employee_hire_sp;



create or replace PROCEDURE updating_employee(
    p_employee_id HR_employees.employee_id%TYPE,
    p_email HR_employees.email%TYPE,
    p_salary HR_employees.salary%TYPE,
    p_phone HR_employees.phone_number%TYPE
)
IS
BEGIN
    UPDATE HR_EMPLOYEES set
    email = p_email,
    salary = p_salary,
    phone_number = p_phone
    WHERE
    employee_id = p_employee_id;
    COMMIT;
END updating_employee;



CREATE OR REPLACE PROCEDURE new_job (
    p_jobid IN hr_jobs.job_id%TYPE,
    p_title IN hr_jobs.job_title%TYPE,
    v_minsal IN hr_jobs.min_salary%TYPE) IS
    v_maxsal hr_jobs.max_salary%TYPE := 2 * v_minsal;
    
BEGIN
    INSERT INTO hr_jobs (job_id, job_title, min_salary, max_salary)
    VALUES (p_jobid, p_title, v_minsal, v_maxsal);
    DBMS_OUTPUT.PUT_LINE('New row added to JOBS table:');
    DBMS_OUTPUT.PUT_LINE(p_jobid || ' ' || p_title || ' ' || v_minsal || ' ' || v_maxsal);

END new_job;



create or replace TRIGGER check_salary_trg
BEFORE INSERT OR UPDATE OF job_id, salary
ON HR_EMPLOYEES
FOR EACH ROW 
BEGIN 
    check_salary(:new.job_id, :new.salary);
END;

COMMIT;

create or replace TRIGGER hire_emp
BEFORE INSERT ON HR_employees
FOR EACH ROW

BEGIN
  SELECT HR_employees_seq.NEXTVAL
  INTO   :new.employee_id
  FROM   dual;
END;