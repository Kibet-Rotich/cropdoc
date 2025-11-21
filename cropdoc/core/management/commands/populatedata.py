import os
import django
import random

# --- CONFIGURATION ---
# Replace 'your_project_name' with your actual project's name
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cropdoc.settings") 
django.setup()

# Replace 'core' with your actual app name if it's different
from core.models import Crop, CropDisease, DiseaseTreatment 

print("--- Starting Data Population for Maize ---")


# 1. ENSURE MAIZE CROP EXISTS (The Fix)
MAIZE_CROP_NAME = "Maize"
try:
    crop, created = Crop.objects.get_or_create(
        crop_name=MAIZE_CROP_NAME,
        # REMOVE the 'description' field here:
        # defaults={'description': 'A cereal grain, also known as corn.'} 
    )
    if created:
        print(f"✅ Created new Crop: {crop.crop_name}")
    else:
        print(f"✅ Found existing Crop: {crop.crop_name}")

except Exception as e:
    print(f"❌ Error during Crop creation/lookup: {e}")
    # Stop the script if the crop cannot be set up
    exit()

# 2. DUMMY DISEASES DATA
diseases_data = [
    {
        "name": "Grey Leaf Spot",
        "characteristics": "Small, rectangular, gray lesions on leaves, typically restricted by leaf veins."
    },
    {
        "name": "Common Rust",
        "characteristics": "Reddish-brown, dusty pustules on both sides of leaves, often more severe on lower leaves."
    },
    {
        "name": "Northern Leaf Blight",
        "characteristics": "Long, elliptical, grayish-green to tan lesions that look like cigar spots."
    },
    {
        "name": "Fall Armyworm",
        "characteristics": "Large, ragged holes in leaves, noticeable feeding damage in the whorl or near the ear. Larvae have an inverted 'Y' on their head."
    },
    {
        "name": "Northern Leaf Spot",
        "characteristics": "Circular to oval spots, often with a tan center and a dark purple or brown border. Can resemble eyespots."
    }
]


# 3. DUMMY TREATMENTS DATA
treatment_templates = [
    {
        "name": "Mancozeb 75DF (Fungicide)",
        "instructions": "Mix 25g in 20L water. Apply as a preventive spray every 7–10 days."
    },
    {
        "name": "Copper Oxychloride (Fungicide)",
        "instructions": "Apply 2.5g per liter of water weekly at the first sign of disease."
    },
    {
        "name": "Propiconazole (Fungicide)",
        "instructions": "Spray at early stages of disease development, 10ml per 20L water."
    },
    {
        "name": "Vector Control (Insecticide)",
        "instructions": "Apply systemic insecticide (e.g., Imidacloprid) to control leafhoppers which transmit the virus."
    },
    {
        "name": "Resistant Varieties (Cultural)",
        "instructions": "Plant resistant or tolerant maize varieties to minimize infection."
    }
]

# 4. INSERT DISEASES AND TREATMENTS
for disease in diseases_data:
    # Use get_or_create to prevent duplicating diseases if the script is run multiple times
    d_obj, created_disease = CropDisease.objects.get_or_create(
        crop=crop,
        disease_name=disease["name"],
        defaults={
            "disease_characteristics": disease["characteristics"]
        }
    )
    if created_disease:
        print(f"\nCreated disease: {d_obj.disease_name}")
    else:
        print(f"\nFound existing disease: {d_obj.disease_name} (Skipping creation)")


    # Add a random subset of treatments to the disease for realistic data
    # Shuffling the templates ensures a different set of treatments each time (optional)
    random.shuffle(treatment_templates)
    
    # Select 2 to 3 treatments for each disease
    treatments_to_add = treatment_templates[:random.randint(2, 3)] 

    for treatment in treatments_to_add:
        # Use get_or_create to prevent duplicating treatments
        t_obj, created_treatment = DiseaseTreatment.objects.get_or_create(
            disease=d_obj,
            crop=crop,
            drug_name=treatment["name"],
            defaults={
                "drug_administration_instructions": treatment["instructions"]
            }
        )
        if created_treatment:
            print(f"  -> Added treatment: {t_obj.drug_name}")
        # else:
        #     print(f"  -> Treatment already exists: {t_obj.drug_name}")

print("\n--- Dummy data populated successfully. ---")