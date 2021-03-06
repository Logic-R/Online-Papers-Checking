# Generated by Django 3.0.8 on 2021-05-22 07:53

from django.db import migrations, models
import django.db.models.deletion
import nlp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WModels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='models', validators=[nlp.models.file_extension])),
                ('subj', models.ForeignKey(db_column='subj', on_delete=django.db.models.deletion.DO_NOTHING, to='Database.Courses')),
            ],
        ),
    ]
