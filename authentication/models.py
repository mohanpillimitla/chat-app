from django.db import models


from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager as AbstractUserManager



class UserManager(AbstractUserManager):
  pass

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True,blank=True)
    


    USERNAME_FIELD = 'username'
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.username)

    objects = UserManager()