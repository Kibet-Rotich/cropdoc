import os
import django
import pandas as pd
from django.core.management.base import BaseCommand, CommandError 

# --- CONFIGURATION ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cropdoc.settings") 
django.setup()

from core.models import Crop, CropDisease, DiseaseTreatment

# Define the required mapping from CSV names to your standardized class names
DISEASE_NAME_MAP = {
    'Fall armyworm (pest)': 'Fall Army Worm',
    'Common Rust (Fungal)': 'Common Rust',
    'Northern Leaf Blight (Fungal)': 'Northern Leaf Blight',
    'Gray Leaf Spot (Fungal)': 'Grey Leaf Spot',
    'Northern Leaf Spot (Fungal)': 'Northern Leaf Spot',
    'Healthy': 'Healthy',
}

# --- Management Command Class ---
class Command(BaseCommand):
    help = 'Populates the database with initial Crop, CropDisease, and DiseaseTreatment data from a CSV file.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting New Data Population for Maize Diseases ---"))
        
        # 1. DELETE EXISTING DATA
        self.stdout.write("\n--- Cleaning Database ---")
        
        # Delete all DiseaseTreatment records
        treatment_count, _ = DiseaseTreatment.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"🧹 Deleted {treatment_count} existing DiseaseTreatment records."))
        
        # Delete all CropDisease records
        disease_count, _ = CropDisease.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"🧹 Deleted {disease_count} existing CropDisease records."))
        
        self.stdout.write(self.style.SUCCESS("✅ Database cleaned successfully."))

        # 2. ENSURE MAIZE CROP EXISTS
        MAIZE_CROP_NAME = "Maize"
        try:
            maize_crop, created = Crop.objects.get_or_create(
                crop_name=MAIZE_CROP_NAME,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created new Crop: {maize_crop.crop_name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ Found existing Crop: {maize_crop.crop_name}"))

        except Exception as e:
            raise CommandError(f"❌ Error during Crop creation/lookup: {e}") 

        # 3. READ DATA FROM CSV
        try:
            df = pd.read_csv('data.csv')
            df = df.fillna('') # Convert NaNs to empty strings
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(df)} records from data.csv."))
        except FileNotFoundError:
            raise CommandError("❌ Error: 'data.csv' not found. Ensure it is in the same directory as manage.py or provide a full path.")
        except Exception as e:
            raise CommandError(f"❌ Error reading data.csv: {e}")

        # 4. INSERT NEW DATA
        self.stdout.write("\n--- Inserting New Disease and Treatment Data ---")
        diseases_inserted = 0
        treatments_inserted = 0
        
        for index, row in df.iterrows():
            csv_disease_name = row['Disease'].strip()
            
            # Look up the standardized name
            standard_disease_name = DISEASE_NAME_MAP.get(csv_disease_name)
            
            if not standard_disease_name:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipping unknown disease in CSV: {csv_disease_name}"))
                continue

            # Combine Symptoms and Prevention into one text field for the model
            characteristics_text = (
                f"**Symptoms:** {row['Symptoms'].strip()}\n\n"
                f"**Prevention:** {row['Prevention'].strip()}"
            )
            
            try:
                # 🟢 CropDisease Insertion (Mapping to disease_characteristics)
                disease = CropDisease.objects.create(
                    crop=maize_crop,
                    disease_name=standard_disease_name,
                    # Maps Symptoms/Prevention to disease_characteristics
                    disease_characteristics=characteristics_text, 
                )
                diseases_inserted += 1
                self.stdout.write(f"  ➕ Created Disease: {disease.disease_name}")

                # Create the DiseaseTreatment entry
                if row['Treatment']:
                    # 🟢 DiseaseTreatment Insertion (Mapping to drug_administration_instructions)
                    DiseaseTreatment.objects.create(
                        disease=disease,
                        crop=maize_crop, # Required foreign key
                        drug_name=f"Recommended Treatment for {disease.disease_name}", # Mapping to drug_name
                        drug_administration_instructions=row['Treatment'].strip() # Mapping 'Treatment' column
                    )
                    treatments_inserted += 1
                    self.stdout.write(f"  ➕ Created Treatment for: {disease.disease_name}")
                
            except Exception as e:
                # Use self.stderr.write for errors
                self.stderr.write(self.style.ERROR(f"❌ Error inserting data for {standard_disease_name}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Data population complete."))
        self.stdout.write(f"  Total Diseases Inserted: {diseases_inserted}")
        self.stdout.write(f"  Total Treatments Inserted: {treatments_inserted}")