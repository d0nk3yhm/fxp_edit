from flask import Flask, request, send_file
import json
import os
import hashlib
import struct
import traceback
import vstplugin

app = Flask(__name__)

# Initialize the plugin (modify plugin_path as required)
plugin_path = './Serum_x64.dll'
plugin = vstplugin.VSTPlugin(plugin_path)
plugin.open()  # Open once and keep it open

def generate_fxp(json_file_path, fxp_output_path):
    # Load parameters from the formatted JSON file
    with open(json_file_path, 'r') as json_file:
        parameters = json.load(json_file)

    fxp_buffer = bytearray()
    
    # Iterate through parameters and set them in the plugin by their index
    for index, (param_name, value) in enumerate(parameters.items()):
        plugin.set_parameter(int(index), float(value))

    # The rest of your code for generating the fxp file
    chunk_data = plugin.get_chunk()
    chunk_magic = b"CcnK"
    fx_magic = b"FPCh"
    version = 1
    fx_id = 0x58667358  # Replace with actual plugin ID
    fx_version = 1
    num_programs = 1
    name = "PresetName".encode("ascii")  # Replace with desired preset name
    chunk_size = len(chunk_data)

    fxp_buffer += struct.pack(">4sI4sIIII28sI", chunk_magic, 0, fx_magic, version, fx_id, fx_version, num_programs, name, chunk_size)
    fxp_buffer += chunk_data
    byte_size = len(fxp_buffer) - 8  # Subtract the size of chunk_magic and byte_size fields
    fxp_buffer[4:8] = struct.pack(">I", byte_size)

    with open(fxp_output_path, "wb") as fxp_file:
        fxp_file.write(fxp_buffer)

def convert_json_to_fxp(json_data, json_file_path, fxp_output_path):
    # Save JSON data to a file
    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file)

    # Generate the fxp file
    generate_fxp(json_file_path, fxp_output_path)

    return fxp_output_path

@app.route('/api', methods=['POST'])
def api_endpoint():
    if request.is_json:
        json_data = request.get_json()

        # Generate a unique file name for JSON and FXP
        hash_suffix = hashlib.sha256(os.urandom(32)).hexdigest()[:8]
        json_file_name = f'data_{hash_suffix}.json'
        fxp_file_name = f'output_{hash_suffix}.fxp'

        # Convert JSON to FXP
        fxp_file_path = convert_json_to_fxp(json_data, json_file_name, fxp_file_name)

        # Send back the .fxp file
        return send_file(fxp_file_path, as_attachment=True)
    else:
        return {"message": "Request must be JSON"}, 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
