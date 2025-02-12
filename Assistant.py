import subprocess as sp
import speech_recognition as sr
import pyttsx3
import platform
import google.generativeai as genai  
import os
import re
import uuid

genai.configure(api_key="Your Api Key")
engine = pyttsx3.init()

def text_to_audio(text):
    engine.say(text)
    engine.runAndWait()

def understand_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio).lower()
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition.")
        return None

def get_sys_details():
    sys_details = (
        f"System: {platform.system()}, "
        f"Node: {platform.node()}, "
        f"Release: {platform.release()}, "
        f"Version: {platform.version()}, "
        f"Machine: {platform.machine()}, "
        f"Processor: {platform.processor()}"
    )
    print("\n🔹 System Details:", sys_details)
    return sys_details

def clean_generated_code(response):
    response = response.strip()
    response = re.sub(r"^```[a-zA-Z0-9]*\n?", "", response)
    response = re.sub(r"\n```$", "", response)
    return response.strip()

def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return clean_generated_code(response.text)
    except Exception as e:
        print("Error:", e)
        return None

def create_valid_filename(prompt, extension):
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', prompt[:20])
    unique_id = uuid.uuid4().hex[:6]
    return f"{clean_name}_{unique_id}.{extension}"

def save_code_to_file(code, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(code)
    print(f"\n✅ Code saved as {filename}")

def run_code_file(filename):
    print(f"\n🔹 Running {filename}...\n")
    try:
        output = sp.getstatusoutput(f"python {filename}")
        print("\n🔹 Execution Output:\n", output[1])
        return output[1]
    except Exception as e:
        print("❌ Error executing the file:", e)
        return None

def open_application(command):
    app_dict = {
        "notepad": "notepad.exe" if platform.system() == "Windows" else "gedit",
        "calculator": "calc.exe" if platform.system() == "Windows" else "gnome-calculator",
        "chrome": "chrome.exe" if platform.system() == "Windows" else "google-chrome"
    }
    
    for app, exe in app_dict.items():
        if app in command:
            try:
                os.system(exe)
                text_to_audio(f"Opening {app}")
                return
            except Exception as e:
                print(f"❌ Error opening {app}: {e}")
                text_to_audio(f"Sorry, I couldn't open {app}.")
                return
    
    text_to_audio("Application not found in my database.")

def ai_assistant():
    sys_details = get_sys_details()
    user_input = understand_voice()
    
    if user_input:
        if "code" in user_input or "program" in user_input or "script" in user_input:
            static_text = "If user is asking for code then generate only the code without extra text."
            final_prompt = f"{user_input}\n\nSystem Details: {sys_details}\n\n{static_text}"
            ai_response = generate_response(final_prompt)

            if ai_response:
                task_filename = create_valid_filename(user_input, "py")
                save_code_to_file(ai_response, task_filename)
                task_output = run_code_file(task_filename)
                
                if task_output:
                    verify_prompt = f"Generate a Python script to verify the output of the following script. If verification is successful, print 'Success', otherwise print 'Failure'.\n\nScript Output:\n{task_output}\n\n{static_text}"
                    verification_script = generate_response(verify_prompt)
                    
                    if verification_script:
                        verify_filename = create_valid_filename("verify_" + user_input, "py")
                        save_code_to_file(verification_script, verify_filename)
                        run_code_file(verify_filename)
                else:
                    print("❌ No output to verify.")
                    text_to_audio("Script execution failed. No output to verify.")
        
        elif "open" in user_input:
            open_application(user_input)
        
        elif "system details" in user_input:
            text_to_audio(sys_details)
        
        else:
            ai_response = generate_response(user_input)
            if ai_response:
                print("Assistant:", ai_response)
                text_to_audio(ai_response)
            else:
                text_to_audio("Sorry, I couldn't process your request.")

ai_assistant()
