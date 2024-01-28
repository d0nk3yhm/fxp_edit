import sys
import struct
import json
import vstplugin

def read_fxp(fxp_file_path):
    with open(fxp_file_path, 'rb') as fxp_file:
        return fxp_file.read()

def apply_parameters_to_plugin(plugin, parameters):
    for index, value in parameters.items():
        try:
            param_value = float(value.split(': ')[1])
            plugin.set_parameter(int(index), param_value)
        except ValueError as e:
            print(f"Error applying parameter: index={index}, value={value}, error={e}")

def generate_fxp(plugin, parameters, fxp_output_path):
    fxp_buffer = bytearray()
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
    byte_size = len(fxp_buffer) - 8
    fxp_buffer[4:8] = struct.pack(">I", byte_size)
    with open(fxp_output_path, "wb") as fxp_file:
        fxp_file.write(fxp_buffer)

def main(json_file_path, fxp_output_path):
    plugin_path = './Serum_x64.dll'
    plugin = vstplugin.VSTPlugin(plugin_path)

    try:
        plugin.open()

        # Load JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Set the chunk data from JSON into the plugin
        if "chunk" in data:
            chunk_data = bytes(data["chunk"])
            plugin.set_chunk(chunk_data)

        # Apply parameters to the plugin
        apply_parameters_to_plugin(plugin, data["parameters"])

        # Generate FXP file
        generate_fxp(plugin, data["parameters"], fxp_output_path)

        print(f"FXP file generated successfully at {fxp_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            # plugin.close()
            print("Plugin closed successfully.")
        except Exception as close_exception:
            print("Error closing the plugin:", close_exception)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fxp_generator.py <json_file_path> <fxp_output_path>")
        sys.exit(1)

    json_path = sys.argv[1]
    fxp_output_path = sys.argv[2]
    main(json_path, fxp_output_path)
