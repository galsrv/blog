# Generated by Django 5.1.4 on 2025-02-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_blog_content_alter_blogger_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='image',
            field=models.ImageField(default='default_image.jpg', upload_to='images/'),
        ),
    ]
