from django.db import migrations

def split_characteristics(apps, schema_editor):
    CropDisease = apps.get_model('core', 'CropDisease')

    for disease in CropDisease.objects.all():
        text = disease.disease_characteristics or ""

        # Initialize empty values
        symptoms = ""
        prevention = ""

        # Parse data if formatted like your example
        if "**Symptoms:**" in text:
            try:
                symptoms = text.split("**Symptoms:**")[1].split("**Prevention:**")[0].strip()
            except:
                symptoms = ""

        if "**Prevention:**" in text:
            try:
                prevention = text.split("**Prevention:**")[1].strip()
            except:
                prevention = ""

        disease.symptoms = symptoms
        disease.prevention = prevention
        disease.save()

def reverse(apps, schema_editor):
    pass  # we don't need rollback logic

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_cropdisease_prevention_cropdisease_symptoms_and_more'),
    ]

    operations = [
        migrations.RunPython(split_characteristics, reverse),
    ]
