import datetime
from datetime import timedelta
from fractions import Fraction

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func, or_

from employees import Employee, Leaves
from leave_forms import (
    CalculateEarnedLeaveForm,
    CasualLeaveForm,
    EarnedLeaveForm,
    EmployeeForm,
    LeaveEncashmentForm,
    LOPLeaveForm,
    RestrictedLeaveform,
    SickLeaveForm,
    SpecialLeaveForm,
)


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

        exists = (
            db.session.query(Employee.id)
            .filter(
                Employee.emp_number == emp_number,
            )
            .first()
        )

        if exists:
            flash("Employee number %s already exists." % emp_number)

        else:

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
    from server import db

    if request.method == "POST":
        # payments = db.get_payments()

        employee.count_casual_leave = 12
        employee.count_restricted_history = 2
        employee.count_sick_leave = min(employee.count_sick_leave + 30, 240)

        # TODO: calculate earned leave as on dec-31 of the year
        employee.history_casual_leave = ""
        employee.history_restricted_holiday = ""
        db.session.add(employee)
        db.session.commit()

        return render_template("employee_page.html", employee=employee)

    return render_template("employee_page.html", employee=employee)


def leave_to_database(
    emp_number, start_date, end_date, nature_of_leave, type_leave, leave_letter_status
):

    from server import db

    leave_list = []

    for dt in daterange(start_date, end_date):
        leave_list.append(dt)

    for dt in leave_list:
        leave = Leaves(
            emp_number=emp_number,
            date_of_leave=dt,
            nature_of_leave=nature_of_leave,
            type_leave=type_leave,
            leave_letter_status=leave_letter_status,
        )
        db.session.add(leave)
        db.session.commit()


def add_lop_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = LOPLeaveForm()
    if form.validate_on_submit():
        type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        if end_date < start_date:
            flash("End date should be higher than start date.")

        else:
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

                no_of_days = numOfDays(start_date, end_date) + 1
                #            if type_leave == "full":
                #                no_of_days = no_of_days * 2

                #            if check_leave_count(employee.count_sick_leave, no_of_days):
                #                employee.count_sick_leave = update_leave(
                #                    employee.count_sick_leave, no_of_days
                #                )

                history_update = "{}: {} (From {} to {})".format(
                    type_leave.title(), str(no_of_days), str(start_date), str(end_date)
                )

                if employee.history_special_leave != None:
                    employee.history_special_leave = (
                        employee.history_special_leave + "<br>" + history_update
                    )
                else:
                    employee.history_special_leave = history_update

                db.session.add(employee)

                nature_of_leave = type_leave

                leave_to_database(
                    employee.emp_number,
                    start_date,
                    end_date,
                    nature_of_leave,
                    None,
                    leave_letter_status,
                )

                return redirect(url_for("employee_page", emp_key=employee.id))
    #            else:
    #
    #               flash("Insufficient leave balance.")

    return render_template("leave_add_lop_leave.html", employee=employee, form=form)


def add_special_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = SpecialLeaveForm()
    if form.validate_on_submit():
        type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        if end_date < start_date:
            flash("End date should be higher than start date.")

        else:
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

                no_of_days = numOfDays(start_date, end_date) + 1
                #            if type_leave == "full":
                #                no_of_days = no_of_days * 2

                #            if check_leave_count(employee.count_sick_leave, no_of_days):
                #                employee.count_sick_leave = update_leave(
                #                    employee.count_sick_leave, no_of_days
                #                )

                history_update = "{}: {} (From {} to {})".format(
                    type_leave.title(), str(no_of_days), str(start_date), str(end_date)
                )

                if employee.history_special_leave != None:
                    employee.history_special_leave = (
                        employee.history_special_leave + "<br>" + history_update
                    )
                else:
                    employee.history_special_leave = history_update

                db.session.add(employee)

                nature_of_leave = type_leave

                leave_to_database(
                    employee.emp_number,
                    start_date,
                    end_date,
                    nature_of_leave,
                    None,
                    leave_letter_status,
                )

                return redirect(url_for("employee_page", emp_key=employee.id))
    #            else:
    #
    #               flash("Insufficient leave balance.")

    return render_template("leave_add_special_leave.html", employee=employee, form=form)


def add_earned_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = EarnedLeaveForm()
    if form.validate_on_submit():
        # type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        leave_updated_date = datetime.datetime.strptime(
            employee.leave_as_on, "%Y-%m-%d"
        ).date()

        if start_date < leave_updated_date:
            flash("Earned leave already updated upto: %s" % employee.leave_as_on)
        else:

            if end_date < start_date:
                flash("End date should be higher than start date.")

            else:

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

                    no_of_days = numOfDays(start_date, end_date) + 1
                    #                if type_leave == "full":
                    #                    no_of_days = no_of_days * 2

                    calculate_el_emp(
                        employee.emp_number, start_date
                    )  # , end_date, False)
                    if check_leave_count(employee.count_earned_leave, no_of_days):
                        employee.count_earned_leave = update_leave(
                            employee.count_earned_leave, no_of_days
                        )
                        employee.leave_as_on = end_date

                        history_update = "EL: {} (From {} to {})".format(
                            str(no_of_days),
                            str(start_date),
                            str(end_date),
                        )

                        if employee.history_earned_leave != None:
                            employee.history_earned_leave = (
                                employee.history_earned_leave + "<br>" + history_update
                            )
                        else:
                            employee.history_earned_leave = history_update

                        db.session.add(employee)

                        nature_of_leave = "Earned leave"

                        leave_to_database(
                            employee.emp_number,
                            start_date,
                            end_date,
                            nature_of_leave,
                            None,
                            leave_letter_status,
                        )

                        return redirect(url_for("employee_page", emp_key=employee.id))
                    else:

                        flash("Insufficient leave balance.")

    return render_template("leave_add_earned_leave.html", employee=employee, form=form)


def calculate_el_emp(emp_number, start_date):  # , end_date, notfromthere):

    # we are going to update earned leave balance of an employee just before we are going to add new earned leave
    # this is to make sure the employee doesn't go over their 270 or something like that
    # sick leave will not contribute to earned leave accruing
    # same for earned leave also
    # we will set the last update of earned leave to the final leave of earned leave hopefully

    from server import db

    emp_key = (
        db.session.query(Employee.id).filter(Employee.emp_number == emp_number).first()
    )
    employee = Employee.query.get_or_404(emp_key)

    tuple_leave_updated_date = (
        db.session.query(Employee.leave_as_on)
        .filter(Employee.emp_number == emp_number)
        .all()
    )
    str_leave_updated_date = [x[0] for x in tuple_leave_updated_date]
    print(str_leave_updated_date[0])

    leave_updated_date = datetime.datetime.strptime(
        str_leave_updated_date[0], "%Y-%m-%d"
    ).date()

    # an employee will accrue earned leave when he/she is "on duty"
    # all leaves other than casual leave, quarantine leave, examination leave and trade union leave
    #  to be excluded when calculating earned leave

    # major leaves to be discounted for calculation of earned leaves are the following:
    # 1. sick leave
    # 2. earned leave
    # 3. strike
    # 4. LOP
    # 5. maternity leave
    # 6. paternity leave

    # counting number of ineligible leaves

    filter_conditions = [
        Leaves.nature_of_leave == "Sick leave",
        Leaves.nature_of_leave == "Earned leave",
        Leaves.nature_of_leave == "LOP",
        Leaves.nature_of_leave == "Strike",
        Leaves.nature_of_leave == "Paternity",
        Leaves.nature_of_leave == "Maternity",
    ]
    count_ineligible_days = (
        db.session.query(func.count(Leaves.id))
        .filter(
            Leaves.emp_number == emp_number, Leaves.date_of_leave >= leave_updated_date
        )
        .filter(or_(*filter_conditions))
        .scalar()
    )

    print(count_ineligible_days)

    no_of_days = numOfDays(leave_updated_date, start_date)

    no_of_days_duty = no_of_days - count_ineligible_days
    accrued_earned_leave = no_of_days_duty / 11

    new_el_balance = float(accrued_earned_leave) + float(employee.count_earned_leave)

    employee.leave_as_on = start_date
    employee.count_earned_leave = min(new_el_balance, 270)

    db.session.add(employee)
    db.session.commit()


def calc_earned_leave_page(emp_key):

    pass

    employee = Employee.query.get_or_404(emp_key)
    form = CalculateEarnedLeaveForm()
    if form.validate_on_submit():
        start_date = form.data["start_date"]
        leave_updated_date = datetime.datetime.strptime(
            employee.leave_as_on, "%Y-%m-%d"
        ).date()

        if start_date < leave_updated_date:
            flash("Earned leave already updated upto: %s" % employee.leave_as_on)
        else:
            calculate_el_emp(employee.emp_number, start_date)  # , start_date, False)
            return redirect(url_for("employee_page", emp_key=employee.id))

    return render_template("calculate_earned_leave.html", employee=employee, form=form)


def add_leave_encashment(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = LeaveEncashmentForm()
    if form.validate_on_submit():
        block_year = form.data["block_year"]
        start_date = form.data["start_date"]
        encashed_days = form.data["encashed_days"]

        leave_updated_date = datetime.datetime.strptime(
            employee.leave_as_on, "%Y-%m-%d"
        ).date()

        if start_date < leave_updated_date:
            flash("Earned leave already updated upto: %s" % employee.leave_as_on)

        else:
            # if block year already taken, then no more leave encashment
            #  date_of_encash =
            if (
                not db.session.query(Leaves.date_of_leave)
                .filter(
                    Leaves.emp_number == employee.emp_number,
                    Leaves.nature_of_leave == "Leave encashment",
                    Leaves.type_leave == block_year,
                )
                .first()
            ):

                calculate_el_emp(employee.emp_number, start_date)  # , end_date, False)
                if check_leave_count(employee.count_earned_leave, encashed_days):
                    employee.count_earned_leave = update_leave(
                        employee.count_earned_leave, encashed_days
                    )
                    employee.leave_as_on = start_date

                    history_update = "Leave encashment: Block year {} {} days (On {})".format(
                        block_year,
                        str(encashed_days),
                        str(start_date),
                        # str(end_date),
                    )

                    if employee.history_leave_encashment != None:
                        employee.history_leave_encashment = (
                            employee.history_leave_encashment + "<br>" + history_update
                        )
                    else:
                        employee.history_leave_encashment = history_update

                    db.session.add(employee)

                    nature_of_leave = "Leave encashment"

                    leave_to_database(
                        employee.emp_number,
                        start_date,
                        start_date,
                        nature_of_leave,
                        block_year,
                        None,
                    )

                    return redirect(url_for("employee_page", emp_key=employee.id))
                else:

                    flash("Insufficient leave balance.")
            else:
                flash(
                    "Block year %s already availed." % block_year
                )  # , date_of_encash.date_of_leave))

    return render_template(
        "leave_add_leave_encashment.html", employee=employee, form=form
    )


def add_sick_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = SickLeaveForm()
    if form.validate_on_submit():
        type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        if end_date < start_date:
            flash("End date should be higher than start date.")

        else:

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

                no_of_days = numOfDays(start_date, end_date) + 1
                if type_leave == "full":
                    no_of_days = no_of_days * 2

                if check_leave_count(employee.count_sick_leave, no_of_days):
                    employee.count_sick_leave = update_leave(
                        employee.count_sick_leave, no_of_days
                    )

                    history_update = "{}: {} (From {} to {})".format(
                        type_leave.title(),
                        str(no_of_days),
                        str(start_date),
                        str(end_date),
                    )

                    if employee.history_sick_leave != None:
                        employee.history_sick_leave = (
                            employee.history_sick_leave + "<br>" + history_update
                        )
                    else:
                        employee.history_sick_leave = history_update

                    db.session.add(employee)

                    nature_of_leave = "Sick leave"

                    leave_to_database(
                        employee.emp_number,
                        start_date,
                        end_date,
                        nature_of_leave,
                        type_leave,
                        leave_letter_status,
                    )

                    return redirect(url_for("employee_page", emp_key=employee.id))
                else:

                    flash("Insufficient leave balance.")

    return render_template("leave_add_sick_leave.html", employee=employee, form=form)


def add_rh_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = RestrictedLeaveform()

    if form.validate_on_submit():
        #  type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = start_date
        leave_letter_status = form.data["leave_letter"]

        if end_date < start_date:
            flash("End date should be higher than start date.")

        else:
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

                no_of_days = numOfDays(start_date, end_date) + 1
                # if type_leave == "half":
                #   no_of_days = no_of_days / 2

                if check_leave_count(employee.count_restricted_holiday, no_of_days):
                    employee.count_restricted_holiday = update_leave(
                        employee.count_restricted_holiday, no_of_days
                    )

                    history_update = "RH: {} (On {})".format(
                        str(no_of_days), str(start_date)
                    )

                    if employee.history_restricted_holiday != None:
                        employee.history_restricted_holiday = (
                            employee.history_restricted_holiday
                            + "<br>"
                            + history_update
                        )
                    else:
                        employee.history_restricted_holiday = history_update

                    db.session.add(employee)

                    nature_of_leave = "Restricted holiday"

                    leave_to_database(
                        employee.emp_number,
                        start_date,
                        end_date,
                        nature_of_leave,
                        None,
                        leave_letter_status,
                    )

                    return redirect(url_for("employee_page", emp_key=employee.id))
                else:

                    flash("Insufficient leave balance.")
    return render_template("leave_add_rh_leave.html", employee=employee, form=form)


def add_casual_leave(emp_key):
    from server import db

    employee = Employee.query.get_or_404(emp_key)
    form = CasualLeaveForm()
    if form.validate_on_submit():
        type_leave = form.data["type_leave"]
        start_date = form.data["start_date"]
        end_date = form.data["end_date"]
        leave_letter_status = form.data["leave_letter"]

        if end_date < start_date:
            flash("End date should be higher than start date.")

        else:

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

                no_of_days = numOfDays(start_date, end_date) + 1
                if type_leave == "half":
                    no_of_days = no_of_days / 2

                if check_leave_count(employee.count_casual_leave, no_of_days):
                    employee.count_casual_leave = update_leave(
                        employee.count_casual_leave, no_of_days
                    )

                    history_update = "{}: {} (From {} to {})".format(
                        type_leave.title(),
                        str(no_of_days),
                        str(start_date),
                        str(end_date),
                    )

                    if employee.history_casual_leave != None:
                        employee.history_casual_leave = (
                            employee.history_casual_leave + "<br>" + history_update
                        )
                    else:
                        employee.history_casual_leave = history_update

                    db.session.add(employee)

                    nature_of_leave = "Casual leave"

                    leave_to_database(
                        employee.emp_number,
                        start_date,
                        end_date,
                        nature_of_leave,
                        type_leave,
                        leave_letter_status,
                    )

                    return redirect(url_for("employee_page", emp_key=employee.id))
                else:

                    flash("Insufficient leave balance.")

    return render_template("leave_add_casual_leave.html", employee=employee, form=form)
