from django.db import models

# Create your models here.
"""
        strategy parameters in order :
        (ticker, period, interval,
        rsi_length, rsi_high, rsi_low,
        macd_fast, macd_slow,
        ema_length,
        trend_line_window, # number of candles to consider
        trend_lever, # change accordingly to average ticker shift)
        """


class SimStrategy(models.Model):

    ticker = models.CharField(max_length=10)
    period = models.CharField(max_length=5)
    rsi_length = models.IntegerField(blank=True, null=True)
    rsi_high = models.IntegerField(blank=True, null=True)
    rsi_low = models.IntegerField(blank=True, null=True)
    macd_fast = models.IntegerField(blank=True, null=True)
    macd_slow = models.IntegerField(blank=True, null=True)
    ema_length = models.IntegerField(blank=True, null=True)
    trend_line_win = models.IntegerField(blank=True, null=True)
    trend_lever = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class SimStats(models.Model):

    start_time = models.DateTimeField()
    win_ratio = models.DecimalField(max_digits=7, decimal_places=2)
    wins = models.IntegerField(blank=True, null=True)
    losses = models.IntegerField(blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=10)
    strategy = models.ForeignKey(SimStrategy, null=True, on_delete=models.SET_NULL)


class SimResults(models.Model):

    direction = models.IntegerField()
    open_val = models.DecimalField(max_digits=10, decimal_places=10)
    close_val = models.DecimalField(max_digits=10, decimal_places=10)
    win = models.BooleanField(default=False)
    loss = models.BooleanField(default=False)
    date = models.DateTimeField()
    profit = models.DecimalField(max_digits=10, decimal_places=10)
    strategy = models.ForeignKey(SimStrategy, null=True, on_delete=models.SET_NULL)

