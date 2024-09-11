import pathlib


def parse_flawfinder_output(input_file: pathlib.Path):
    result_list = []

    with input_file.open('r') as infile:
        for line in infile:
            parts = line.split(':')
            if len(parts) >= 3:
                file_path = parts[0].strip()
                line_number = parts[1].strip()

                try:
                    with open(file_path, "r") as source_file:
                        lines = source_file.readlines()
                        vulnerability_line = lines[int(line_number) - 1].strip()  # zero-indexed
                except (FileNotFoundError, IndexError) as e:
                    vulnerability_line = f"Error retrieving line: {e}"

                result = {
                    'file_path': file_path,
                    'line_number': int(line_number),
                    'vulnerability_line': vulnerability_line,
                }
                result_list.append(result)

    return result_list
