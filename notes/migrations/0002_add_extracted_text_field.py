from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studymaterial',
            name='extracted_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
