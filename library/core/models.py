from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_membership = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    # Add related_name to avoid clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',  # Unique name for core.User reverse accessor
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_set',  # Unique name for core.User reverse accessor
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='core_user',
    )

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(r'^\d{13}$', 'ISBN must be 13 digits')]
    )
    published_date = models.DateField()
    copies_available = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title