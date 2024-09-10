import json
import pathlib


def parse_flawfinder_output(input_file: pathlib.Path, output_file: pathlib.Path):
    result_list = []

    with input_file.open('r') as infile:
        for line in infile:
            parts = line.split(':')
            if len(parts) >= 3:
                file_path = parts[0].strip()
                line_number = parts[1].strip()

                remaining = ':'.join(parts[2:]).strip()

                risk_and_description = remaining.split(']')
                if len(risk_and_description) >= 2:
                    risk_level = risk_and_description[0].strip('[').strip()
                    description_and_comment = risk_and_description[1].strip()

                    description_parts = description_and_comment.split(':', 1)
                    description = description_parts[0].strip()
                    comment = description_parts[1].strip() if len(description_parts) > 1 else ''

                    result = {
                        'file_path': file_path,
                        'line_number': int(line_number),
                        'risk_level': int(risk_level),
                        'description': description,
                        'comment': comment
                    }
                    result_list.append(result)

    # Optionally, write the results to the output JSON file
    with output_file.open('w') as outfile:
        json.dump(result_list, outfile, indent=4)

    return result_list
