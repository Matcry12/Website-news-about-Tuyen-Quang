# Generated by Django 4.2.15 on 2024-08-15 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_new_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='new',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
