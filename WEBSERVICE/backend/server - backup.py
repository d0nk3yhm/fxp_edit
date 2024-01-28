from flask import Flask, request, send_file, jsonify, render_template
import os
import hashlib
import struct
import vstplugin
import json
import re

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

temp_files_dir = './temp_files'
if not os.path.exists(temp_files_dir):
    os.makedirs(temp_files_dir)

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

def apply_parameters_to_plugin(plugin, parameters):
    for index, value_str in parameters.items():
        value = float(value_str.split(': ')[1])
        plugin.set_parameter(int(index), value)

def generate_fxp(plugin, parameters, original_fxp_path, fxp_output_path, preset_name="NewPreset"):
    original_fxp_data = read_fxp(original_fxp_path)
    chunk_magic = b"CcnK"
    fx_magic = b"FPCh"
    version = 1
    fx_id = 0x58667358  # Replace with actual plugin ID
    fx_version = 1
    num_programs = 1
    name = preset_name.encode("ascii").ljust(28, b'\x00')
    apply_parameters_to_plugin(plugin, parameters)
    updated_chunk_data = plugin.get_chunk()
    chunk_size = len(updated_chunk_data)

    fxp_buffer = bytearray(struct.pack(">4sI4sIIII28sI", chunk_magic, 0, fx_magic, version, fx_id, fx_version, num_programs, name, chunk_size))
    fxp_buffer += updated_chunk_data
    byte_size = len(fxp_buffer) - 8
    fxp_buffer[4:8] = struct.pack(">I", byte_size)

    with open(fxp_output_path, "wb") as fxp_file:
        fxp_file.write(fxp_buffer)

@app.route('/upload-fxp-endpoint', methods=['POST'])
def upload_fxp():
    if 'fxp-file' in request.files:
        fxp_file = request.files['fxp-file']
        original_fxp_file_name = f'original_{hashlib.sha256(os.urandom(32)).hexdigest()[:8]}.fxp'
        original_fxp_file_path = os.path.join(temp_files_dir, original_fxp_file_name)
        fxp_file.save(original_fxp_file_path)
        json_data = {"parameters": extract_parameters(plugin)}
        return jsonify(json_data)
    else:
        return {"message": "No FXP file provided"}, 400

@app.route('/api', methods=['POST'])
def api_endpoint():
    if request.is_json:
        json_data = request.get_json()
        fxp_output_file_name = f'modified_{hashlib.sha256(os.urandom(32)).hexdigest()[:8]}.fxp'
        fxp_output_path = os.path.join('./modified_fxp_files', fxp_output_file_name)
        original_fxp_files = sorted([f for f in os.listdir(temp_files_dir) if f.startswith('original_')])
        if not original_fxp_files:
            return {"message": "No original FXP file available"}, 400
        latest_original_fxp_file = original_fxp_files[-1]
        original_fxp_file_path = os.path.join(temp_files_dir, latest_original_fxp_file)
        preset_name = json_data.get("preset_name", "NewPreset")
        generate_fxp(plugin, json_data["parameters"], original_fxp_file_path, fxp_output_path, preset_name)
        return send_file(fxp_output_path, as_attachment=True)
    else:
        return {"message": "Request must be JSON"}, 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
