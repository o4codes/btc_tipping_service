# Generated by Django 4.0.3 on 2022-03-29 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_lightningtransaction_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lightningtransaction',
            name='reference',
            field=models.CharField(default='20455b1b-043e-42c2-a323-1b453519d3f7', max_length=100),
        ),
    ]
