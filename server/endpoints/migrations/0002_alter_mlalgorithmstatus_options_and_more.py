# Generated by Django 4.0.3 on 2022-03-27 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('endpoints', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mlalgorithmstatus',
            options={'verbose_name_plural': 'MLAlgorithmStatuses'},
        ),
        migrations.AlterField(
            model_name='mlalgorithm',
            name='code',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='mlalgorithm',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='mlalgorithmstatus',
            name='status',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='mlrequest',
            name='feedback',
            field=models.TextField(blank=True, default='', max_length=10000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mlrequest',
            name='full_response',
            field=models.TextField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='mlrequest',
            name='input_data',
            field=models.TextField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='mlrequest',
            name='response',
            field=models.TextField(max_length=10000),
        ),
    ]