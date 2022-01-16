from django.db import models
from django.contrib.auth.models import User

#数据库中的一个表对应这里的一个类，表中的一行对应类的一个对象

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # 当user删掉时，和user关联的player也一块删掉
    photo = models.URLField(max_length=256, blank=True)

    def __str__(self):
        return str(self.user)
