from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import uuid

COMPLAINT_STATUS = [
    ("Pending", "Pending"),
    ("In Progress", "In Progress"),
    ("Closed", "Closed"),
    ("Escalated", "Escalated")
]

class BaseInfoModel(models.Model):
    """
    Base fields for all model
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_updated",
        null=True,
    )
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseInfoModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=65)
    is_active = models.BooleanField(default=True)
    is_employee = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)


class UserLoginSession(BaseInfoModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    login_datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    logout_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-login_datetime']

    def __str__(self):
        return f"{self.user.username} - {self.login_datetime}"


class EmployeeCheckIn(BaseInfoModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    checkin_datetime = models.DateTimeField(auto_now_add=True)
    checkout_datetime = models.DateTimeField(null=True, blank=True)
    checkin_location = models.CharField(max_length=255, blank=True, null=True)
    checkout_location = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # True if checked in, False if checked out

    class Meta:
        ordering = ['-checkin_datetime']

    def __str__(self):
        return f"{self.user.username} - {self.checkin_datetime}"

    @property
    def duration(self):
        """Calculate duration of check-in session"""
        if self.checkout_datetime:
            return self.checkout_datetime - self.checkin_datetime
        return None

    @property
    def is_checked_in(self):
        """Check if employee is currently checked in"""
        return self.is_active and not self.checkout_datetime

    def get_formatted_duration(self):
        """Return formatted duration string"""
        if not self.duration:
            return "-"
        
        total_seconds = self.duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if self.duration.days > 0:
            return f"{self.duration.days}d {hours}h {minutes}m"
        else:
            return f"{hours}h {minutes}m"


class Complaints(BaseInfoModel):
    object_id = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name='Public identifier',
    )
    title = models.CharField(max_length=200)
    complainant_name = models.CharField(max_length=100, verbose_name="Complainant Name", blank=True, null=True)
    complaint = models.TextField()
    assignee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="%(app_label)s_%(class)s_author",
        null=True, 
        blank=True
    )
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(choices=COMPLAINT_STATUS, default="Pending")

    def __str__(self):
        return self.title

