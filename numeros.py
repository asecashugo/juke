# Generate Spanish audio clips (1–67) using pyttsx3 (offline TTS)
import pyttsx3
import os
import zipfile

# Spanish numbers 1–67
numbers_es = [
    "uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve","diez",
    "once","doce","trece","catorce","quince","dieciséis","diecisiete","dieciocho","diecinueve","veinte",
    "veintiuno","veintidós","veintitrés","veinticuatro","veinticinco","veintiséis","veintisiete","veintiocho","veintinueve","treinta",
    "treinta y uno","treinta y dos","treinta y tres","treinta y cuatro","treinta y cinco","treinta y seis","treinta y siete","treinta y ocho","treinta y nueve","cuarenta",
    "cuarenta y uno","cuarenta y dos","cuarenta y tres","cuarenta y cuatro","cuarenta y cinco","cuarenta y seis","cuarenta y siete","cuarenta y ocho","cuarenta y nueve","cincuenta",
    "cincuenta y uno","cincuenta y dos","cincuenta y tres","cincuenta y cuatro","cincuenta y cinco","cincuenta y seis","cincuenta y siete","cincuenta y ocho","cincuenta y nueve","sesenta",
    "sesenta y uno","sesenta y dos","sesenta y tres","sesenta y cuatro","sesenta y cinco","sesenta y seis","sesenta y siete"
]

# concat "capitulo_" + number

numbers_es = [f"capitulo {num}" for num in numbers_es]

# Setup directory
base_dir = "/mnt/data/spanish_numbers_audio"
os.makedirs(base_dir, exist_ok=True)

engine = pyttsx3.init()

# Try to set Spanish voice if available
voices = engine.getProperty('voices')
for v in voices:
    if "spanish" in v.name.lower() or "es_" in v.id.lower():
        engine.setProperty('voice', v.id)
        break

# Generate files
file_paths = []
for i, word in enumerate(numbers_es, start=1):
    file_path = os.path.join(base_dir, f"{i:02d}_{word}.wav")
    engine.save_to_file(word, file_path)
    file_paths.append(file_path)

engine.runAndWait()

# Zip all files
zip_path = "/mnt/data/spanish_numbers_1_67_mp3.zip"
with zipfile.ZipFile(zip_path, 'w') as z:
    for fp in file_paths:
        z.write(fp, os.path.basename(fp))

zip_path