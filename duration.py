import calendar
import collections
import datetime


_DAYS_IN_WEEK = 7
_MONTHS_IN_YEAR = 12


class _BASE_UNIT(object):

  _MONTH_LENGTH = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

  @classmethod
  def _MonthLength(cls, year, month):
    if month == 2 and calendar.isleap(year):
      return 29
    return cls._MONTH_LENGTH[month]
    
  @staticmethod
  def _ShowQuantity(x, singular, plural):
    if x == 1:
      return '%d %s' % (x, singular)
    return '%d %s' % (x, plural)

  @classmethod
  def _Normalize(cls, year, month, day):
    max_day = cls._MonthLength(year, month)
    return datetime.date(year, month, min(day, max_day))
    

class _DAY(_BASE_UNIT):

  @staticmethod
  def Count(start_date, end_date):
    return end_date.toordinal() - start_date.toordinal()

  @staticmethod
  def AddTo(orig_date, x):
    return datetime.date.fromordinal(orig_date.toordinal() + x)

  @classmethod
  def ToString(cls, x):
    return cls._ShowQuantity(x, 'day', 'days')
      

class _WEEK(_BASE_UNIT):

  @staticmethod
  def Count(start_date, end_date):
    return _DAY.Count(start_date, end_date) / _DAYS_IN_WEEK

  @staticmethod
  def AddTo(orig_date, x):
    return _DAY.AddTo(orig_date, _DAYS_IN_WEEK * x)

  @classmethod
  def ToString(cls, x):
    return cls._ShowQuantity(x, 'week', 'weeks')
      

class _MONTH(_BASE_UNIT):

  @classmethod
  def Count(cls, start_date, end_date):
    start_months = _MONTHS_IN_YEAR * start_date.year + start_date.month 
    end_months = _MONTHS_IN_YEAR * end_date.year + end_date.month
    if end_date.day >= start_date.day or end_date.day == cls._MonthLength(end_date.year, end_date.month):
      return end_months - start_months
    return end_months - start_months - 1

  @classmethod
  def AddTo(cls, orig_date, x):
    months = _MONTHS_IN_YEAR * orig_date.year + orig_date.month + x - 1
    return cls._Normalize(months / _MONTHS_IN_YEAR, months % _MONTHS_IN_YEAR + 1, orig_date.day)

  @classmethod
  def ToString(cls, x):
    return cls._ShowQuantity(x, 'month', 'months')
      

class _YEAR(_BASE_UNIT):

  @staticmethod
  def Count(start_date, end_date):
    return _MONTH.Count(start_date, end_date) / _MONTHS_IN_YEAR

  @staticmethod
  def AddTo(orig_date, x):
    return _MONTH.AddTo(orig_date, _MONTHS_IN_YEAR * x)

  @classmethod
  def ToString(cls, x):
    return cls._ShowQuantity(x, 'year', 'years')
      

class Duration(collections.namedtuple('Duration', 'year month week day')):
  """Duration represents a fixed length of time in years, months, weeks, days.

  Duration objects are immutable. Duration objects support equals and not
  equals, but they do not support comparision operators.
  """
  __slots__ = ()

  def __new__(cls, year=0, month=0, week=0, day=0):
    return tuple.__new__(cls, (year, month, week, day))

  def With(self, **kwargs):
    """With returns a new Duration object with specified fields changed.

    Example usage: new_value = old_value.With(day=1).
    """
    for x in kwargs:
      if kwargs[x] != getattr(self, x):
        return self._replace(**kwargs)
    return self

  def Normalize(self):
    """Normalize normalizes this Duration object and returns the result.

    For example 47 days => 6 weeks 5 days; 13 months => 1 year 1 month.
    But note that 1 month 47 days => 1 month 47 days as the number of days in
    a month changes.
    """
    months = _MONTHS_IN_YEAR * self.year + self.month
    days = _DAYS_IN_WEEK * self.week + self.day
    return self.With(year=months / _MONTHS_IN_YEAR, month=months % _MONTHS_IN_YEAR, week=days / _DAYS_IN_WEEK, day=days % _DAYS_IN_WEEK)

  @staticmethod
  def _ForPeriod(
      start_date, end_date, has_big, has_small,
      big_unit, small_unit, smalls_in_big):
    if has_small:
      units = small_unit.Count(start_date, end_date)
      start_date = small_unit.AddTo(start_date, units)
      if has_big:
        return units / smalls_in_big, units % smalls_in_big, start_date
      return 0, units, start_date
    elif has_big:
      units = big_unit.Count(start_date, end_date)
      start_date = big_unit.AddTo(start_date, units)
      return units, 0, start_date
    else:
      return 0, 0, start_date

  @classmethod
  def ForPeriod(cls, start_date, end_date, prototype):
    """ForPeriod returns the time between start_date and end_date.

    start_date and end_date are datetime.date objects. prototype is a
    Duration object that is a template for the Duration object to be returned.
    For instance, if prototype == Duration(month=1, day=1) then the returned
    Duration will be in months and days.
    """
    year, month, start_date = cls._ForPeriod(
        start_date, end_date, prototype.year, prototype.month, _YEAR, _MONTH, _MONTHS_IN_YEAR)
    week, day, _ = cls._ForPeriod(
        start_date, end_date, prototype.week, prototype.day, _WEEK, _DAY, _DAYS_IN_WEEK)
    return Duration(year=year, month=month, week=week, day=day)
      

  def Add(self, rhs, multiply=1):
    """Add adds a Duration object to this one returning the result.

    If multiply is set, then the result will be self + (rhs * multiply).
    """
    return Duration(
        year=self.year + rhs.year * multiply,
        month=self.month + rhs.month * multiply,
        week=self.week + rhs.week * multiply,
        day=self.day + rhs.day * multiply) 

  def _ApproxDays(self):
    return (self.year + self.month / 12.0) * 365.2425 + self.week * 7.0 + self.day * 1.0

  def Count(self, start_date, end_date):
    """Count computes how many of this Duration can fit between start_date and end_date.

    start_date and end_date are datetime.date objects; the result is an
    integer. 
    """
    period_in_days = end_date.toordinal() - start_date.toordinal()
    approx_days = self._ApproxDays()
    result = int(period_in_days / approx_days)
    while self.AddTo(start_date, multiply=result) < end_date:
      result += 1
    while self.AddTo(start_date, multiply=result) > end_date:
      result -= 1
    return result

  def AddTo(self, orig_date, multiply=1):
    """AddTo adds this Duration to orig_date returning the result.

    orig_date is a datetime.date. If multiply is set, the result is
    orig_date + (self * multiply)
    """
    result = orig_date
    months = (_MONTHS_IN_YEAR * self.year + self.month) * multiply
    if months:
      result = _MONTH.AddTo(result, months)
    days = (_DAYS_IN_WEEK * self.week + self.day) * multiply
    if days:
      result = _DAY.AddTo(result, days)
    return result
    
  def __str__(self):
    units = ((self.year, _YEAR), (self.month, _MONTH), (self.week, _WEEK), (self.day, _DAY))
    return ', '.join(unit.ToString(x) for x, unit in units if x)

  def __repr__(self):
    units = ((self.year, 'year'), (self.month, 'month'), (self.week, 'week'), (self.day, 'day'))
    return 'duration.Duration(%s)' % ', '.join('%s=%s' % (unit, x) for x, unit in units if x)

YEAR = Duration(year=1)
MONTH = Duration(month=1)
WEEK = Duration(week=1)
DAY = Duration(day=1)
ZERO = Duration()

