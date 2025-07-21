import os
import django
import random

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")  # Replace with your project name
django.setup()

from core.models import Crop, CropDisease, DiseaseTreatment  # Replace with your app name

# Ensure crop exists
crop = Crop.objects.get(pk=1)  # Assume maize

# Dummy diseases
diseases_data = [
    {
        "name": "Gray Leaf Spot",
        "characteristics": "Small, rectangular, gray lesions on leaves."
    },
    {
        "name": "Common Rust",
        "characteristics": "Reddish-brown pustules on both sides of leaves."
    },
    {
        "name": "Northern Corn Leaf Blight",
        "characteristics": "Long, elliptical, grayish-green lesions on leaves."
    },
    {
        "name": "Maize Streak Virus",
        "characteristics": "Chlorotic streaks along leaf veins."
    },
    {
        "name": "Downy Mildew",
        "characteristics": "White fungal growth and leaf chlorosis."
    }
]

# Dummy treatments
treatment_templates = [
    {
        "name": "Mancozeb 75DF",
        "instructions": "Mix 25g in 20L water. Spray every 7–10 days."
    },
    {
        "name": "Copper Oxychloride",
        "instructions": "Apply 2.5g per liter of water weekly."
    },
    {
        "name": "Propiconazole",
        "instructions": "Spray at early signs, 10ml per 20L water."
    },
    {
        "name": "Chlorothalonil",
        "instructions": "Apply preventively every 10 days."
    },
    {
        "name": "Carbendazim",
        "instructions": "Use 1g per liter at disease onset."
    }
]

# Insert diseases and treatments
for disease in diseases_data:
    d_obj = CropDisease.objects.create(
        crop=crop,
        disease_name=disease["name"],
        disease_characteristics=disease["characteristics"]
    )
    print(f"Created disease: {d_obj.disease_name}")

    for treatment in treatment_templates:
        t_obj = DiseaseTreatment.objects.create(
            disease=d_obj,
            crop=crop,
            drug_name=treatment["name"],
            drug_administration_instructions=treatment["instructions"]
        )
        print(f"  -> Added treatment: {t_obj.drug_name}")
print("Dummy data populated successfully.")