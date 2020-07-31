# Generated by Django 3.0.6 on 2020-07-31 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0004_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tweet.Tweet'),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
