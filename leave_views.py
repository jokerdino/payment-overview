from datetime import timedelta
from fractions import Fraction

from flask import flash, redirect, render_template, url_for

from employees import Employee, Leaves
from leave_forms import EmployeeForm, LeaveForm


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def numOfDays(date1, date2):
    return (date2 - date1).days


def mixed_to_float(x):
    """Function credit to https://stackoverflow.com/a/46303199"""
    return float(sum(Fraction(term) for term in x.split()))


def check_leave_count(leave_balance, no_of_days):

    #    current_leave_balance = d[emp_no][leave_type]
    # employee = Employee.query.get_or_404(emp_key)
    # current_leave_balance = employee.leave_type
    if (float(leave_balance) - float(no_of_days)) < 0:
        # print("Insufficient leave balance.")
        return False
    else:
        return True


def update_leave(leave_balance, no_of_days):

    # current_balance = d[emp_no][leave_type]
    newbalance = float(leave_balance) - float(no_of_days)
    return newbalance

    # d[emp_no][leave_type] = newbalance
    # save_data()


#   if leave_type != "earned leave":

#      print("%s has been updated. New balance: %s" % (leave_type, newbalance))
# elif leave_type == "earned leave":
#    mixed_frac = dec_to_proper_frac(emp_no)
#   print("%s has been updated. New balance: %s" % (leave_type, mixed_frac))


def dec_to_proper_frac(emp_no):

    earned_leave = float(d[emp_no]["earned leave"])

    if not (earned_leave).is_integer():

        a = int(earned_leave)
        new = earned_leave - a
        b = Fraction(new % 11).limit_denominator(100)
        fraction = str(a) + " " + str(b)
        return fraction
    else:
        return earned_leave


def leave_project():
    return render_template("leave_home.html")


def show_all_employees():
    return render_template("all_employees.html", employees=Employee.query.all())


def create_employee():
    from server import db

    form = EmployeeForm()
    if form.validate_on_submit():
        emp_number = form.data["emp_number"]
        name = form.data["name"]
        leave_as_on = form.data["leave_as_on"]

        casual_leave = max(0, min(float(form.data["casual_leave"]), 12))
        #           casual_leave = max(0,min(int(casual_leave), 12))

        earned_leave = form.data["earned_leave"]
        #  print(mixed_to_float(earned_leave))
        earned_leave = mixed_to_float(earned_leave)
        earned_leave = max(0, (min(float(earned_leave), 270)))

        restricted_holiday = max(0, min(int(form.data["restricted_holiday"]), 2))

        #   RH = max(0,min(int(RH),2))
        sick_leave = max(0, min(int(form.data["sick_leave"]), 240))
        #    sick_leave = max(0,min(int(sick_leave),240))

        employee = Employee(
            emp_number=emp_number,
            name=name,
            leave_as_on=leave_as_on,
            count_casual_leave=casual_leave,
            count_earned_leave=earned_leave,
            count_restricted_holiday=restricted_holiday,
            count_sick_leave=sick_leave,
        )

        db.session.add(employee)
        db.session.commit()

        return redirect(url_for("employee_page", emp_key=employee.id))

    return render_template("new_employee.html", form=form)


def employee_page(emp_key):
    employee = Employee.query.get_or_404(emp_key)

    return render_template("employee_page.html", employee=employee)


def add_casual_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = LeaveForm()
    if form.validate_on_submit():
        type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        # ensure leave is not already entered before - done for start date
        # check sufficient leave balance - done
        # expand leaves - done
        # add leaves - done
        # update leave balance - done

        exists = (
            db.session.query(Leaves.date_of_leave)
            .filter(
                Leaves.date_of_leave == start_date,
                Leaves.emp_number == employee.emp_number,
            )
            .first()
        )

        if exists:

            flash("Leave already entered.")

        else:
            # print("does not exist yet")

            no_of_days = numOfDays(start_date, end_date) + 1
            if type_leave == "half":
                no_of_days = no_of_days / 2

            if check_leave_count(employee.count_casual_leave, no_of_days):
                employee.count_casual_leave = update_leave(
                    employee.count_casual_leave, no_of_days
                )

                history_update = "{}: {} (From {} to {})".format(
                    type_leave.title(), str(no_of_days), str(start_date), str(end_date)
                )

                if employee.history_casual_leave != None:
                    employee.history_casual_leave = (
                        employee.history_casual_leave + "<br>" + history_update
                    )
                else:
                    employee.history_casual_leave = history_update

                db.session.add(employee)

                nature_of_leave = "Casual leave"
                casual_leave_list = []

                for dt in daterange(start_date, end_date):
                    casual_leave_list.append(dt)

                for dt in casual_leave_list:
                    leave = Leaves(
                        emp_number=employee.emp_number,
                        date_of_leave=dt,
                        nature_of_leave=nature_of_leave,
                        type_leave=type_leave,
                        leave_letter_status=leave_letter_status,
                    )
                    db.session.add(leave)
                    db.session.commit()

                return redirect(url_for("employee_page", emp_key=employee.id))
            else:

                flash("Insufficient leave balance.")

    return render_template("leave_add_casual_leave.html", employee=employee, form=form)