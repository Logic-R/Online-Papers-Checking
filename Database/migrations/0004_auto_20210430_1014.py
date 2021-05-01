# Generated by Django 3.0.8 on 2021-04-30 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Database', '0003_auto_20210420_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultstubject',
            name='marks',
            field=models.FloatField(db_column='Marks'),
        ),
        migrations.AlterField(
            model_name='resultstubject',
            name='percentage',
            field=models.FloatField(db_column='Percentage'),
        ),
        migrations.AlterField(
            model_name='resultstubject',
            name='subject',
            field=models.ForeignKey(db_column='Subject', on_delete=django.db.models.deletion.DO_NOTHING, to='Database.Courses'),
        ),
    ]