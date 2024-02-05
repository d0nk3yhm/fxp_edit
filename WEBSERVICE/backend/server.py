# FXP edit - A web application for editing and applying FXP files
# Copyright (C) 2024 d0nk3yhm
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import threading
import time
import uuid
from flask import Flask, request, send_file, abort, jsonify, render_template

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


print("-------------------------------------------------------------")
print("FXP Edit Copyright (C) 2024 d0nk3yhm")
print("This program comes with ABSOLUTELY NO WARRANTY.")
print("This is free software, and you are welcome to redistribute it")
print("under certain conditions. see http://www.gnu.org/licenses/")
print("-------------------------------------------------------------")


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
        unique_id = uuid.uuid4().hex
        fxp_file_name = f'original_{unique_id}.fxp'
        fxp_file_path = os.path.join(temp_files_dir, fxp_file_name)
        fxp_file.save(fxp_file_path)

        fxp_data = read_fxp(fxp_file_path)
        header_data = list(fxp_data[:60])
        chunk_data = list(fxp_data[60:])

        json_file_name = f'data_{unique_id}.json'
        json_file_path = os.path.join(json_files_dir, json_file_name)

        parameters = extract_parameters(plugin)  # directly return the dictionary of parameters

        data = {
            "header": header_data,
            "parameters": parameters,
            "chunk": chunk_data
        }

        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return jsonify({
            "parameters": parameters,
            "json_file_name": json_file_name,
            "unique_id": unique_id
        })
    else:
        return jsonify({"message": "No FXP file provided"}), 400






def generate_fxp(json_file_path, modified_fxp_file_path):
    print(f"(inside generate_fxp) Processing: json_file_path: {json_file_path}, modified_fxp_file_path: {modified_fxp_file_path}")
    app.logger.info(f"(inside generate_fxp) Processing: json_file_path: {json_file_path}, modified_fxp_file_path: {modified_fxp_file_path}")
    try:
        process = subprocess.Popen(
            ['python', 'fxp_generator.py', json_file_path, modified_fxp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # Log stdout for debugging subprocess output
        if stdout:
            app.logger.info(f"FXP Generator subprocess stdout: {stdout.decode().strip()}")

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            app.logger.error(f"FXP Generator subprocess error: {error_message}")
            return {"message": f"Error generating FXP: {error_message}"}, 500

        return True
    except Exception as e:
        app.logger.error(f"Exception in FXP Generator subprocess: {e}")
        return {"message": f"Error generating FXP: {str(e)}"}, 500






@app.route('/api', methods=['POST'])
def api_endpoint():
    if not request.is_json:
        app.logger.error("Request body is not JSON")
        return jsonify(message="Request must be JSON"), 400

    json_data = request.get_json()
    #app.logger.debug(f"Received JSON data: {json_data}")

    listen_only = json_data.get('listen', False)
    json_file_name = json_data.get('json_file_name', '')
    updated_parameters = json_data.get('parameters', {})
    unique_id = json_data.get('unique_id', str(uuid.uuid4().hex))

    json_file_path = os.path.join(json_files_dir, json_file_name)
    if not os.path.exists(json_file_path):
        app.logger.error(f"JSON file not available: {json_file_path}")
        return jsonify(message="JSON file not available"), 400

    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        data['parameters'] = updated_parameters

        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        app.logger.error(f"Error processing JSON file: {e}")
        return jsonify(message="Error processing JSON file"), 500

    modified_fxp_file_name = f'{unique_id}_modified.fxp'
    app.logger.info(f"modified_fxp_file_name: {modified_fxp_file_name}")
    modified_fxp_file_path = os.path.join(modified_fxp_dir, modified_fxp_file_name)
    app.logger.info(f"modified_fxp_file_path: {modified_fxp_file_path}")

    app.logger.info(f"Sending to generate_fxp: {json_file_path} {modified_fxp_file_path}")
    try:
        result = generate_fxp(json_file_path, modified_fxp_file_path)
        if isinstance(result, tuple):
            app.logger.error(f"FXP generation error: {result[0]}")
            return jsonify(result[0]), result[1]
    except Exception as e:
        app.logger.error(f"Unhandled exception in FXP generation: {e}")
        return jsonify(message="Error generating FXP"), 500

    if listen_only:
        app.logger.info(f"FXP modifications applied for listening. unique_id: {unique_id}")
        return jsonify({"message": "FXP modifications applied for listening.", "unique_id": unique_id})
    else:
        app.logger.info(f"Sending modified FXP file: {modified_fxp_file_path}")
        return send_file(modified_fxp_file_path, as_attachment=True)

    

@app.route('/play', methods=['GET'])
def play_note():
    note = request.args.get('note')
    duration = request.args.get('duration', '500')  # Default duration
    unique_id = request.args.get('unique_id')

    # Validate the required parameters
    if not note:
        return jsonify(message="Note parameter is missing"), 400
    if not duration:
        return jsonify(message="Duration parameter is missing"), 400
    if not unique_id:
        return jsonify(message="Unique ID parameter is missing"), 400
    
    if not note or not unique_id:
        abort(400, 'Missing required parameters.')

    midi_file = f"piano/note_{note}_{duration}.mid"
    app.logger.info(f"midi_file: {midi_file}")
    output_wav = os.path.join(temp_files_dir, f"{unique_id}_note_{note}_{duration}.wav")
    app.logger.info(f"output_wav: {output_wav}")
    fxp_file_path = os.path.join(modified_fxp_dir, f"{unique_id}_modified.fxp")
    app.logger.info(f"fxp_file_path: {fxp_file_path}")
    if not os.path.exists(fxp_file_path):
        abort(404, 'Adjusted FXP file not found.')

    cmd = f"mrswatson64.exe --midi-file {midi_file} --output {output_wav} --plugin Serum_x64.dll,{fxp_file_path}"
    subprocess.call(cmd, shell=True)

    threading.Thread(target=delayed_delete, args=(output_wav, 10)).start()

    return send_file(output_wav, as_attachment=False)


def delayed_delete(file_path, delay):
    time.sleep(delay)
    try:
        os.remove(file_path)
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
