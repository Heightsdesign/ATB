from peewee import *
import datetime

# infos at : https://github.com/coleifer/peewee

pg_db = PostgresqlDatabase('atb', user='postgres', password="Eug&nia06240",
                           host='127.0.0.1', port=5432)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = pg_db


class Strategy(BaseModel):

    name = CharField(max_length=100)
    ticker = CharField(max_length=10)
    period = CharField(max_length=5, null=True)
    interval = CharField(max_length=5, null=True)
    rsi_length = IntegerField(null=True)
    rsi_high = IntegerField(null=True)
    rsi_low = IntegerField(null=True)
    macd_fast = IntegerField(null=True)
    macd_slow = IntegerField(null=True)
    ema_length = IntegerField(null=True)
    sma_length = IntegerField(null=True)
    trend_line_win = IntegerField(null=True)
    trend_angle = DecimalField(max_digits=5, decimal_places=2, null=True)
    short_trend_win = IntegerField(null=True)
    short_trend_angle = DecimalField(max_digits=5, decimal_places=2, null=True)
    description = TextField(null=True)
    rsf_n1 = IntegerField(null=True)
    rsf_n2 = IntegerField(null=True)
    n_vol_tp = IntegerField(null=True)
    tp_percentage = IntegerField(null=True)
    sl_percentage = IntegerField(null=True)
    retracement_bar_val = IntegerField(null=True)


# create strategy
strat = Strategy(
    name="EURUSD-1mo-5m-macd-ema-10",
    ticker="EURUSD=X",
    period="1mo",
    interval="5m",
    rsi_length=None,
    rsi_high=None,
    rsi_low=None,
    macd_fast=9,
    macd_slow=26,
    ema_length=200,
    sma_length=200,
    trend_line_win=100,
    trend_angle=10,
    description="First strategy, res/sup strength = 4"
)


class Stats(BaseModel):

    start_time = DateTimeField()
    win_ratio = DecimalField(max_digits=7, decimal_places=2)
    wins = IntegerField(null=True)
    losses = IntegerField(null=True)
    profit = DecimalField(max_digits=15, decimal_places=10)
    strategy = ForeignKeyField(Strategy, null=True)


class Results(BaseModel):

    direction = IntegerField()
    open_val = DecimalField(max_digits=15, decimal_places=10)
    close_val = DecimalField(max_digits=15, decimal_places=10)
    win = BooleanField(default=False)
    loss = BooleanField(default=False)
    date = DateTimeField()
    profit = DecimalField(max_digits=15, decimal_places=10)
    trend_angle = DecimalField(max_digits=8, decimal_places=5, null=True)
    strategy = ForeignKeyField(Strategy, null=True)


pg_db.connect()

# UNCOMMENT TO CREATE TABLES IN DB
# pg_db.create_tables([Strategy, Results, Stats])
# UNCOMMENT TO CREATE STRATEGY
# strat.save()



"""
charlie = User.create(username='charlie')
huey = User(username='huey')
huey.save()

# No need to set `is_published` or `created_date` since they
# will just use the default values we specified.
Tweet.create(user=charlie, message='My first tweet')

# A simple query selecting a user.
User.get(User.username == 'charlie')

# Get tweets created by one of several users.
usernames = ['charlie', 'huey', 'mickey']
users = User.select().where(User.username.in_(usernames))
tweets = Tweet.select().where(Tweet.user.in_(users))
"""