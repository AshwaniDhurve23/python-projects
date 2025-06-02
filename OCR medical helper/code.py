import pytesseract
from PIL import Image
import sched
import time
import pygame
import threading

# Set tesseract cmd path
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ashwa\OneDrive\Desktop\medical helper\tesseract.exe'

# Initialize scheduler and global variables
scheduler = sched.scheduler(time.time, time.sleep)
count = 0
medicine_taken = False  # Flag to stop reminders

# ---------------------- PATIENT DATA SECTION ----------------------

def add_patient_data(patient_data, patient_id, data):
    patient_data[patient_id] = data

def make_decision(patient_data, patient_id):
    data = patient_data.get(patient_id)
    if not data:
        return "Patient data not found."
    if data['age'] > 60:
        return "High risk for cardiovascular disease."
    elif data['temperature'] > 38.0:
        return "Fever detected. Possible infection."
    else:
        return "No significant issues detected."

# ---------------------- OCR FUNCTION ----------------------

def ocr_medical_text(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img)
    return text


# ---------------------- SOUND FUNCTION USING PYGAME ----------------------

def play_reminder_sound():
    pygame.mixer.init()
    sound_file = r"C:\Users\ashwa\OneDrive\Desktop\OCR medical helper\beat_wave.wav"
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

    # Wait until the music finishes playing or medicine taken
    while pygame.mixer.music.get_busy():
        if medicine_taken:
            pygame.mixer.music.stop()
            break
        pygame.time.Clock().tick(10)

# ---------------------- REMINDER FUNCTION ----------------------

def remind_extracted_text(image_path):
    global count, medicine_taken
    if medicine_taken:
        print("Medicine taken. Stopping reminders.")
        return

    count += 1
    print(f"\n Reminder {count}: Don't forget to take your medicine!")
    play_reminder_sound()

    if count < 3:
        scheduler.enter(10, 1, remind_extracted_text, argument=(image_path,))
    else:
        print(" All reminders completed.")

# ---------------------- INPUT LISTENER THREAD ----------------------

def input_listener():
    global medicine_taken
    while True:
        user_input = input("Type 'taken' when you have taken your medicine: ").strip().lower()
        if user_input == "taken":
            medicine_taken = True
            print("Reminder stopped. Glad you took your medicine!")
            break

# ---------------------- MAIN FUNCTION ----------------------

def main():
    global medicine_taken

    patient_data = {}

    # Input patient details
    patient_id = int(input("Enter patient ID: "))
    age = int(input("Enter patient age: "))
    temperature = float(input("Enter patient temperature: "))
    heart_rate = int(input("Enter patient heart rate: "))

    add_patient_data(patient_data, patient_id, {
        'age': age,
        'temperature': temperature,
        'heart_rate': heart_rate
    })

    decision = make_decision(patient_data, patient_id)
    print("\n🩺 Decision for Patient:", decision)

    image_path = r"C:\Users\ashwa\OneDrive\Desktop\OCR medical helper\prescription.png"
    extracted_text = ocr_medical_text(image_path)
    print("\n Extracted Text:\n", extracted_text)

   

    # Start reminder scheduler
    scheduler.enter(10, 1, remind_extracted_text, argument=(image_path,))

    # Start input listener thread for stopping reminders
    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()

    scheduler.run()

# ---------------------- SCRIPT ENTRY POINT ----------------------

if __name__ == "__main__":
    main()

