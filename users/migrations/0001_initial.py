# Generated by Django 3.2.15 on 2023-09-24 20:54

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Farms',
            fields=[
                ('farm_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=2000)),
                ('farm_name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Seasons',
            fields=[
                ('season_id', models.AutoField(primary_key=True, serialize=False)),
                ('season_name', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('job_id', models.AutoField(primary_key=True, serialize=False)),
                ('field_job_type', models.CharField(max_length=255)),
                ('due_date', models.DateField()),
                ('farm_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.farms')),
                ('season_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.seasons')),
            ],
        ),
        migrations.CreateModel(
            name='Fields',
            fields=[
                ('field_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=255)),
                ('farm_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.farms')),
            ],
        ),
        migrations.CreateModel(
            name='FieldJobRecords',
            fields=[
                ('field_job_record_id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.BooleanField()),
                ('field_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.fields')),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.jobs')),
            ],
        ),
        migrations.CreateModel(
            name='CropDataRotation',
            fields=[
                ('crop_rotation_id', models.AutoField(primary_key=True, serialize=False)),
                ('crop_type', models.CharField(max_length=255)),
                ('sown_date', models.DateField()),
                ('harvest_date', models.DateField()),
                ('field_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.fields')),
                ('season_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.seasons')),
            ],
        ),
    ]
