# Generated by Django 5.0.2 on 2024-03-25 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomm', '0003_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(default=True, upload_to='ecomm/image/'),
        ),
    ]
