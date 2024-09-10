import json
import pathlib


def parse_flawfinder_output(input_file="output_txt_file.txt", output_file: pathlib.Path=None):
    results = []

    with open(input_file, 'r') as file:
        for line in file:
            if ':' in line and '[' in line and ']' in line:
                parts = line.split(':', 2)
                file_path = parts[0].strip()
                line_number = parts[1].strip()
                message_parts = parts[2].split('[', 1)
                risk_level = message_parts[1].split(']', 1)[0]
                description = message_parts[1].split(']', 1)[1].strip()

                results.append({
                    "file": file_path,
                    "line": line_number,
                    "risk_level": risk_level,
                    "description": description
                })

    with open(output_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)
