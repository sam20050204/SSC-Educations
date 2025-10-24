# Create this file: core/migrations/0008_bill_billitem.py

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_payment'),  # Update this to match your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_no', models.CharField(editable=False, max_length=20, unique=True)),
                ('bill_date', models.DateField(verbose_name='Bill Date')),
                ('customer_name', models.CharField(max_length=100, verbose_name='Customer Name')),
                ('customer_mobile', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Mobile number must be 10 digits', regex='^\\d{10}$')], verbose_name='Customer Mobile')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Amount')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Bill',
                'verbose_name_plural': 'Bills',
                'db_table': 'bills',
                'ordering': ['-bill_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BillItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200, verbose_name='Item Name')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Quantity')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Rate (per unit)')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.bill', verbose_name='Bill')),
            ],
            options={
                'verbose_name': 'Bill Item',
                'verbose_name_plural': 'Bill Items',
                'db_table': 'bill_items',
                'ordering': ['id'],
            },
        ),
    ]