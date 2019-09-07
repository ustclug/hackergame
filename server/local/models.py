from django.db import models


class UstcFirstBlood(models.Model):
    problem = models.TextField(db_column='name')
    user = models.TextField(db_column='first_blood')

    class Meta:
        db_table = 'ustc_first_blood'
        managed = False
