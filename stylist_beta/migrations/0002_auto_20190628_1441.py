# Generated by Django 2.2.2 on 2019-06-28 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stylist_beta', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogimage',
            name='after_img',
            field=models.ImageField(upload_to='after_img'),
        ),
        migrations.AlterField(
            model_name='catalogimage',
            name='before_img',
            field=models.ImageField(upload_to='before_img'),
        ),
        migrations.AlterField(
            model_name='menu',
            name='img',
            field=models.ImageField(upload_to='menu_img'),
        ),
        migrations.AlterField(
            model_name='stylistprofile',
            name='img',
            field=models.ImageField(upload_to='stylist_img'),
        ),
        migrations.AlterField(
            model_name='stylistprofile',
            name='salon_img',
            field=models.ImageField(upload_to='salon_img'),
        ),
    ]
