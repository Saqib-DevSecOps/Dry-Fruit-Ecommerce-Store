from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_resized import ResizedImageField
from faker import Faker

fake = Faker()

"""
At the start please be careful to start migrations
--------------------------------------------------

STEP: 1 comment current_subscription [FIELD] in model [USER]
STEP: 1 py manage.py makemigrations accounts
STEP: 2 py manage.py migrate
Then do next ...

"""
GENDER_CHOICES = (
    ('1', 'Male'),
    ('2', 'FeMale'),
    ('3', 'Custom'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=200)
    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, size=[250, 250], quality=75, force_format='PNG',
        help_text='size of logo must be 250*250 and format must be png image file', crop=['middle', 'center']
    )
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=False)
    is_client = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ['-id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def name_or_username(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def is_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    def delete(self, *args, **kwargs):
        self.profile_image.delete(save=True)
        super(User, self).delete(*args, **kwargs)

    @classmethod
    def fake(cls, total=10):

        print()
        print("- User: build")
        for count in range(total):
            profile = fake.simple_profile()
            user = User.objects.create_user(
                username=profile['username'],
                email=profile['mail'],
                password=fake.isbn13()
            )
            user.first_name = fake.first_name()
            user.last_name = fake.first_name()
            user.phone_number = fake.msisdn()
            user.save()
            print(f"---- User: {count} faked.")

        print("- END ")
        print()


#



