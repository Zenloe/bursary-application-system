from PIL import Image
import pytesseract
import pytesseract

import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process



# Set the Tesseract executable path directly in your script
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ensure the path is correct

# Test if Tesseract is recognized
print(pytesseract.get_tesseract_version())  # This should print the Tesseract version


def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error in extracting text: {e}")
        return ""



def verify_application(application):
    """Compares extracted document data with student-provided details."""
    
    student_name = application.full_name.lower().strip()
    school_name = application.institution_name.lower().strip()


    extracted_id_text = extract_text_from_image(application.personal_id.path).lower().strip()
    extracted_school_text = extract_text_from_image(application.school_transcript.path).lower().strip()

    print(f"Extracted ID text: {extracted_id_text}")
    print(f"Extracted school text: {extracted_school_text}")


    name_match_score = fuzz.partial_ratio(student_name, extracted_id_text)
    school_match_score = fuzz.partial_ratio(school_name, extracted_school_text)

    MATCH_THRESHOLD = 80

    application.extracted_id_name = extracted_id_text
    application.extracted_school_name = extracted_school_text

    if name_match_score > MATCH_THRESHOLD and school_match_score > MATCH_THRESHOLD:
        application.status = "Approved"
    else:
        application.status = "Flagged"

    
    application.save()




