from django.db import models
from django.contrib.auth.models import AbstractUser
from djongo import models as djongo_models  # Import djongo's models module

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Farms(djongo_models.Model):
    farm_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=2000)
    farm_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Farm {self.farm_id}"


class Fields(djongo_models.Model):
    field_id = models.AutoField(primary_key=True)
    farm_id = models.ForeignKey(Farms, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    coordinates = models.CharField(max_length=2000)
    area = models.CharField(max_length=1000)
    description = models.CharField(max_length=5000)

    def __str__(self):
        return f"Fields {self.field_id}"


class Seasons(djongo_models.Model):
    season_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    season_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Season {self.season_id}"


class CropDataRotation(djongo_models.Model):
    crop_rotation_id = models.AutoField(primary_key=True)
    season_id = models.ForeignKey(Seasons, on_delete=models.CASCADE)
    field_id = models.ForeignKey(Fields, on_delete=models.CASCADE)
    crop_type = models.CharField(max_length=255)
    sown_date = models.DateField()
    harvest_date = models.DateField()

    def __str__(self):
        return f"Crop Rotation {self.crop_rotation_id}"


class Jobs(djongo_models.Model):
    job_id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=255)
    season_id = models.ForeignKey(Seasons, on_delete=models.CASCADE)
    farm_id = models.ForeignKey(Farms, on_delete=models.CASCADE)
    field_job_type = models.CharField(max_length=255)
    input_data = models.CharField(max_length=2000)
    due_date = models.DateField()

    def __str__(self):
        return f"Job {self.job_id}"


class FieldJobRecords(djongo_models.Model):
    field_job_record_id = models.AutoField(primary_key=True)
    field_id = models.ForeignKey(Fields, on_delete=models.CASCADE)
    job_id = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    status = models.BooleanField()
    complete_date = models.DateField()

    def __str__(self):
        return f"Field Job Record {self.field_job_record_id}"
