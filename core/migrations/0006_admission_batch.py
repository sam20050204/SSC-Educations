# core/migrations/0006_admission_batch.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_admission_paid_fees_admission_total_fees'),  # ← FIXED: Changed from '0005_admission_fee_fields'
    ]

    operations = [
        migrations.AddField(
            model_name='admission',
            name='batch',
            field=models.CharField(
                default='2025-01',
                max_length=7,
                verbose_name='Batch (Month-Year)',
                help_text='Batch month and year (e.g., 2025-01 for January 2025)'
            ),
            preserve_default=False,
        ),
    ]