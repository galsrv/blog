# Generated by Django 5.1.4 on 2025-01-16 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_blogger_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogger',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
