import cv2
import face_recognition
import os
import numpy as np
import pandas as pd
import subprocess
from datetime import datetime, timedelta
import sys

# Function to create a new attendance CSV file with the current date and section in the filename
def create_new_attendance_file(section):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    new_attendance_file = os.path.join("attendance_files", f"{date_str}_section_{section}.csv")
    return new_attendance_file

# Ensure the "attendance_files" directory exists
os.makedirs("attendance_files", exist_ok=True)

# Load known faces and their names based on the selected section
selected_section = sys.argv[1] if len(sys.argv) > 1 else 'a'
known_faces_dir = os.path.join("known_faces", f"section_{selected_section}")
known_faces = []
known_names = []

for file in os.listdir(known_faces_dir):
    if file.endswith(".jpg") or file.endswith(".png"):
        image = face_recognition.load_image_file(os.path.join(known_faces_dir, file))
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(os.path.splitext(file)[0])

# Create or load attendance CSV file with the current date and section in the filename
attendance_file = create_new_attendance_file(selected_section)

if os.path.exists(attendance_file):
    attendance_df = pd.read_csv(attendance_file)
else:
    attendance_df = pd.DataFrame(columns=["Name", "Time"])

# Initialize webcam
video_capture = cv2.VideoCapture(0)

# Define the cooldown duration (in seconds) for each face
cooldown_duration = 3600  # Adjust this value as needed
general_time_to_leave = 10  # Time for the user to leave the camera's view

# Initialize variables to track the last recognized face and its attendance status
last_recognized_face = None
attendance_status = None
attendance_status_time = None

while True:
    ret, frame = video_capture.read()

    # Find face locations in the frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    current_time = datetime.now()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the detected face with known faces
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

            # Check if enough time has passed since the last entry for this face
            last_entry_time = attendance_df[(attendance_df['Name'] == name)]['Time'].max()

            if pd.isnull(last_entry_time):
                # Record attendance with timestamps
                timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                new_entry = pd.DataFrame({"Name": [name], "Time": [timestamp]})
                attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
                last_recognized_face = name
                attendance_status = ("Attendance marked successfully", (0, 255, 0))  # Green text
                attendance_status_time = current_time
            else:
                time_difference = current_time - pd.to_datetime(last_entry_time)
                if time_difference.total_seconds() > cooldown_duration + general_time_to_leave:
                    # Record attendance with timestamps
                    timestamp = current_time.strftime("%Y-%m-%d %H:M:S")
                    new_entry = pd.DataFrame({"Name": [name], "Time": [timestamp]})
                    attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
                    last_recognized_face = name
                    attendance_status = ("Attendance marked successfully", (0, 255, 0))  # Green text
                    attendance_status_time = current_time
                else:
                    last_recognized_face = name
                    if (current_time - attendance_status_time).total_seconds() < general_time_to_leave:
                        attendance_status = ("Please step away", (0, 0, 255))  # Red text
                    else:
                        attendance_status = ("Attendance already taken", (0, 0, 255))  # Red text
        else:
            last_recognized_face = None
            attendance_status = None

        # Display the result on the frame
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        if attendance_status:
            text, text_color = attendance_status
            cv2.putText(frame, text, (left, top - 10), font, 0.5, text_color, 1)

    cv2.imshow("Video", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

# Save the attendance to the section-specific CSV file
attendance_file = create_new_attendance_file(selected_section)
attendance_df.to_csv(attendance_file, index=False)

#This next part is totally optional if you don't want to upload attendance on cloud remove the next code

# Run the JavaScript file
js_file = 'upload.js'  # Replace 'your_js_file.js' with the actual filename
subprocess.run(['node', js_file])
