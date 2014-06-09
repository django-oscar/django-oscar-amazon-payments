from django.db import models


class OrderTransaction(models.Model):

    order_number = models.CharField(max_length=128, db_index=True)
