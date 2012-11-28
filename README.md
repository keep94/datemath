datemath
========

Perform arithmetic with python datetime.date objects.

# Figure out how many years, months, days from now until Christmas 2030.

    import datetime
    import duration

    print duration.Duration.ForPeriod(
        datetime.datetime.now().date(),
        datetime.date(2030, 12, 25),
        duration.Duration(year=1, month=1, day=1))

# Find out the next time you will be a multple of 100 weeks old.

    import datetime
    import duration

    your_birthday = datetime.date(1990, 5, 25)
    now = datetime.datetime.now().date()
    dur = duration.Duration(week=100)
    count = dur.Count(your_birthday, now)
    print dur.AddTo(your_birthday, multiply=count + 1)


