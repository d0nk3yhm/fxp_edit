from flask import Flask, request, send_file, jsonify, render_template
import os
import hashlib
import struct
import vstplugin
import json
import re
import subprocess

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

temp_files_dir = './temp_files'
modified_fxp_dir = './modified_fxp_files'
json_files_dir = './json_files'

if not os.path.exists(temp_files_dir):
    os.makedirs(temp_files_dir)
if not os.path.exists(modified_fxp_dir):
    os.makedirs(modified_fxp_dir)
if not os.path.exists(json_files_dir):
    os.makedirs(json_files_dir)

plugin_path = './Serum_x64.dll'
plugin = vstplugin.VSTPlugin(plugin_path)
plugin.open()

@app.route('/')
def index():
    return render_template('index.html')

def read_fxp(fxp_file_path):
    with open(fxp_file_path, 'rb') as fxp_file:
        return fxp_file.read()

def extract_parameters(plugin, total_params=500):
    parameters = {}
    name_count = {}
    for i in range(total_params):
        param_name = plugin.get_parameter_name(i)
        param_value = plugin.get_parameter(i)
        if not param_name or param_name == "---" or param_name == "?param?":
            param_name = f"PSUDO_Param_{i}"
        else:
            param_name = re.sub(r'[^a-zA-Z0-9]', '', param_name)
            if param_name in name_count:
                name_count[param_name] += 1
                param_name += f"_{name_count[param_name]:03d}"
            else:
                name_count[param_name] = 1
        parameters[str(i)] = f"{param_name}: {param_value}"
    return parameters

@app.route('/upload-fxp-endpoint', methods=['POST'])
def upload_fxp():
    if 'fxp-file' in request.files:
        fxp_file = request.files['fxp-file']
        hash_suffix = hashlib.sha256(os.urandom(32)).hexdigest()[:8]
        fxp_file_name = f'original_{hash_suffix}.fxp'
        fxp_file_path = os.path.join(temp_files_dir, fxp_file_name)
        fxp_file.save(fxp_file_path)

        fxp_data = read_fxp(fxp_file_path)
        header_data = list(fxp_data[:60])
        chunk_data = list(fxp_data[60:])

        json_file_name = f'data_{hash_suffix}.json'
        json_file_path = os.path.join(json_files_dir, json_file_name)
        data = {"header": header_data, "parameters": extract_parameters(plugin), "chunk": chunk_data}
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # Return both parameters and json_file_name to frontend
        return jsonify({"parameters": extract_parameters(plugin), "json_file_name": json_file_name})

    else:
        return {"message": "No FXP file provided"}, 400




def generate_fxp(json_file_path, modified_fxp_file_path):
    try:
        # Call fxp_generator.py as a subprocess
        process = subprocess.Popen(
            ['python', 'fxp_generator.py', json_file_path, modified_fxp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Handle any errors that occurred in the subprocess
            error_message = stderr.decode().strip()
            return {"message": f"Error generating FXP: {error_message}"}, 500

        # If the subprocess completed successfully, send the generated FXP file
        return send_file(modified_fxp_file_path, as_attachment=True)
    except Exception as e:
        return {"message": f"Error generating FXP: {str(e)}"}, 500





@app.route('/api', methods=['POST'])
def api_endpoint():
    if request.is_json:
        json_data = request.get_json()
        print(f"Incoming JSON data: {json_data}")
        json_file_name = json_data.get('json_file_name', '')
        updated_parameters = json_data.get('parameters', {}).get('parameters', {})

        print(f"Received update for {json_file_name}: {updated_parameters}")

        json_file_path = os.path.join(json_files_dir, json_file_name)
        if not os.path.exists(json_file_path):
            return {"message": "JSON file not available"}, 400

        # Load the original JSON data
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Replace the entire 'parameters' section with the updated parameters
        data['parameters'] = updated_parameters

        print(f"Updated parameters to be saved: {data['parameters']}")

        # Save the updated JSON data back to the file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Updated parameters saved.")

        # Generate the FXP file
        modified_fxp_file_name = f'modified_{hashlib.sha256(os.urandom(32)).hexdigest()[:8]}.fxp'
        modified_fxp_file_path = os.path.join(modified_fxp_dir, modified_fxp_file_name)
        generate_fxp(json_file_path, modified_fxp_file_path)

        return send_file(modified_fxp_file_path, as_attachment=True)
    else:
        return {"message": "Request must be JSON"}, 400



if __name__ == '__main__':
    app.run(debug=True, port=5000)
