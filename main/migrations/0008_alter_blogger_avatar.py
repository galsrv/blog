# Generated by Django 5.1.4 on 2025-01-16 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_blog_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogger',
            name='avatar',
            field=models.ImageField(default='default_avatar.jpg', upload_to='avatars/'),
        ),
    ]
