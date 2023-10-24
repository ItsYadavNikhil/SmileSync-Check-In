from flask import Flask, render_template, request, session
import subprocess
import sys
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Define the directory where CSV files are stored
attendance_dir = "attendance_files"

# Define a list of valid sections
valid_sections = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

@app.route('/')
def index():
    # Retrieve the selected section from the session if available
    selected_section = session.get('selected_section', None)
    return render_template('index.html', sections=valid_sections, selected_section=selected_section)

@app.route('/run_script', methods=['POST'])
def run_script():
    if request.method == 'POST':
        # Get the selected section from the form
        selected_section = request.form.get('selected_section')

        if selected_section not in valid_sections:
            return render_template('index.html', message="Invalid section selected")

        # Store the selected section in the session
        session['selected_section'] = selected_section

        # Get the path to the Python interpreter within the virtual environment
        python_executable = sys.executable

        # Specify the script to run based on the selected section
        script_to_run = 'attendance_system.py'

        # Append the section as a command-line argument
        script_args = [python_executable, script_to_run, selected_section]

        # Run the script with the section-specific CSV file
        result = subprocess.run(script_args, capture_output=True, text=True)
        output = result.stdout
        return render_template('index.html', script_output=output, sections=valid_sections, selected_section=selected_section)

@app.route('/show_section_attendance', methods=['POST'])
def show_section_attendance():
    if request.method == 'POST':
        # Get the selected section and date to view
        selected_section_view = request.form.get('selected_section_view')
        selected_date = request.form.get('selected_date')

        # Construct the CSV file path for the selected section and date
        csv_file_path = os.path.join(attendance_dir, f"{selected_date}_section_{selected_section_view}.csv")

        # Check if the CSV file exists
        if os.path.exists(csv_file_path):
            # Read the CSV data into a DataFrame
            attendance_df = pd.read_csv(csv_file_path)

            # Convert the DataFrame to an HTML table
            attendance_table = attendance_df.to_html(classes='table table-bordered table-striped', index=False)

            return render_template('index.html', attendance_table=attendance_table, sections=valid_sections, selected_section=session.get('selected_section', None))
        else:
            return render_template('index.html', message="File Not Present", sections=valid_sections, selected_section=session.get('selected_section', None))

if __name__ == '__main__':
    app.run(debug=True)
