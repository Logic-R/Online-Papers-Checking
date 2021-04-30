# Generated by Django 3.0.8 on 2021-04-30 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Database', '0005_auto_20210430_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultstubject',
            name='Examid',
            field=models.ForeignKey(blank=True, db_column='Examid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Database.Exam'),
        ),
        migrations.AlterField(
            model_name='resultstubject',
            name='uniqueid',
            field=models.ForeignKey(blank=True, db_column='Uniqueid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Database.quiz_assignment_id'),
        ),
    ]
