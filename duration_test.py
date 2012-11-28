import unittest
import datetime
import duration

class DurationTest(unittest.TestCase):

  def test_add(self):
    answer = (duration.YEAR
        .Add(duration.MONTH)
        .Add(duration.WEEK)
        .Add(duration.DAY)
        .Add(duration.WEEK))
    self.assertEquals(
        duration.Duration(year=1, month=1, week=2, day=1),
        answer)

  def test_add_2(self):
    d = duration.Duration(month=6)
    answer = d.Add(d)
    self.assertEquals(duration.Duration(month=12), answer)

  def test_add_3(self):
    d = duration.Duration(year=1, month=2, week=3, day=4)
    e = duration.Duration(year=8, month=6, week=4, day=2)
    answer = d.Add(e, 3)
    self.assertEquals(
        duration.Duration(year=25, month=20, week=15, day=10), answer)

  def test_add_to(self):
    d = duration.Duration(year=1, month=2, week=3, day=4)
    answer = d.AddTo(datetime.date(2011, 9, 11))
    self.assertEquals(
        datetime.date(2012, 12, 6),
        answer)

  def test_add_to_2(self):
    d = duration.Duration(year=1, week=1)
    answer = d.AddTo(datetime.date(2011, 9, 11))
    self.assertEquals(
        datetime.date(2012, 9, 18),
        answer)

  def test_add_to_truncate(self):
    d = duration.Duration(year=1, month=2)
    answer = d.AddTo(datetime.date(2012, 2, 29))
    self.assertEquals(
        datetime.date(2013, 4, 29),
        answer)

  def test_add_to_truncate2(self):
    answer = duration.MONTH.AddTo(datetime.date(2012, 1, 31))
    self.assertEquals(
        datetime.date(2012, 2, 29),
        answer)

  def test_normalize_year_month(self):
    d = duration.Duration(month=6)
    answer = d.Add(d).Normalize()
    self.assertEquals(duration.YEAR, answer)

  def test_normalize_year_month_same(self):
    answer = duration.YEAR.Normalize()
    self.assertTrue(duration.YEAR is answer)
      
  def test_normalize_week_day(self):
    d = duration.Duration(week=1, day=4)
    answer = d.Add(d).Normalize()
    self.assertEquals(duration.Duration(week=3,day=1), answer)

  def test_normalize_week_day_same(self):
    d = duration.Duration(week=1, day=4)
    answer = d.Normalize()
    self.assertTrue(d is answer)

  def test_from_period(self):
    answer = duration.Duration.ForPeriod(
        datetime.date(2011, 9, 11),
        datetime.date(2012, 12, 6),
        duration.Duration(year=1, month=1, week=1, day=1))
    self.assertEquals(
        duration.Duration(year=1, month=2, week=3, day=4),
        answer)
    answer = duration.Duration.ForPeriod(
        datetime.date(2011, 9, 11),
        datetime.date(2012, 12, 6),
        duration.Duration(month=1, day=1))
    self.assertEquals(
        duration.Duration(month=14, day=25),
        answer)
    answer = duration.Duration.ForPeriod(
        datetime.date(2011, 9, 11),
        datetime.date(2012, 12, 6),
        duration.Duration(year=1, week=1))
    self.assertEquals(
        duration.Duration(year=1, week=12),
        answer)

  def test_from_period_2(self):
    answer = duration.Duration.ForPeriod(
        datetime.date(2012, 1, 31),
        datetime.date(2012, 2, 29),
        duration.Duration(month=1, day=1))
    self.assertEquals(
        duration.MONTH,
        answer)

  def test_from_period_3(self):
    answer = duration.Duration.ForPeriod(
        datetime.date(2012, 1, 28),
        datetime.date(2012, 2, 29),
        duration.MONTH)
    self.assertEquals(
        duration.MONTH,
        answer)

  def test_from_period_4(self):
    answer = duration.Duration.ForPeriod(
        datetime.date(2012, 2, 29),
        datetime.date(2013, 4, 29),
        duration.Duration(year=1, month=1, day=1))
    self.assertEquals(
        duration.Duration(year=1, month=2),
        answer)

  def test_from_period_5(self):
    answer = duration.Duration.ForPeriod(
        datetime.date(2013, 1, 31),
        datetime.date(2013, 2, 28),
        duration.Duration(month=1, day=1))
    self.assertEquals(
        duration.MONTH,
        answer)

  def test_count(self):
    d = duration.Duration(year=1, week=1)
    self.assertEquals(39, d.Count(datetime.date(1971, 11, 27), datetime.date(2011, 8, 27)))
    self.assertEquals(38, d.Count(datetime.date(1971, 11, 27), datetime.date(2011, 8, 26)))

  def test_approx_days(self):
    answer = duration.Duration(year=4, month=3, week=2, day=1)._ApproxDays()
    self.assertTrue(answer > 1567.28)
    self.assertTrue(answer < 1567.29)

  def test_with(self):
    d = duration.Duration(year=1, month=2, week=3, day=4)
    self.assertTrue(d is d.With())
    self.assertTrue(d is d.With(year=1, month=2, week=3, day=4))
    self.assertEquals(
        duration.Duration(year=4, month=3, week=2, day=1),
        d.With(year=4, month=3, week=2, day=1))

  def test_equals_and_hash(self):
    d = duration.Duration(year=1, month=2, week=3, day=4)
    e = duration.Duration(year=1, month=2, week=3, day=4)
    f = duration.Duration(year=4, month=3, week=2, day=1)
    self.assertTrue(d == d)
    self.assertFalse(d != d)
    self.assertTrue(d == e)
    self.assertFalse(d != e)
    self.assertFalse(d == f)
    self.assertTrue(d != f)
    self.assertFalse(d == 2)
    self.assertTrue(d != 2)
    self.assertEquals(hash(d), hash(e))
    self.assertFalse(hash(d) == hash(f))

  def test_properties(self):
    d = duration.Duration(year=1, month=2, week=3, day=4)
    self.assertEquals(1, d.year)
    self.assertEquals(2, d.month)
    self.assertEquals(3, d.week)
    self.assertEquals(4, d.day)
    self.assertEquals(1, duration.MONTH.month)
    self.assertEquals(0, duration.MONTH.year)

  def test_str(self):
    self.assertEquals(
        '1 year, 1 month, 1 week, 1 day',
        str(duration.Duration(year=1, month=1, week=1, day=1)))
    self.assertEquals(
        '2 years, 3 months, 4 weeks, 5 days',
        str(duration.Duration(year=2, month=3, week=4, day=5)))
    self.assertEquals(
        '2 days',
        str(duration.Duration(day=2)))
    self.assertEquals('', str(duration.ZERO))

  def test_repr(self):
    self.assertEquals(
        'duration.Duration(year=2, month=3, week=4, day=5)',
        repr(duration.Duration(year=2, month=3, week=4, day=5)))
    self.assertEquals(
        'duration.Duration(day=2)',
        repr(duration.Duration(day=2)))
   


    
if __name__ == '__main__':
  unittest.main()

