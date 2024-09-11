import argparse
import json
import pathlib
import subprocess
import time
from typing import Final

from Run_modules.result_saver import parse_flawfinder_output
from Run_modules.run_modules import check_name, clone_repo, RepositoryNotFoundError, remove_all_files, \
    copy_zip_to_directory, extract_archives_in


def analyze_file_with_repo_scraper(file_path: pathlib.Path, output_txt_file: pathlib.Path, verbose=5):
    parsed_results = {}

    unique_results = {level: set() for level in range(verbose + 1)}

    for level in range(verbose + 1):
        print(f"Analyzing for risk level {level}...")

        command = ['flawfinder', '--minlevel', str(level), str(file_path)]
        try:
            with output_txt_file.open('w') as outfile:
                process = subprocess.Popen(command, stdout=outfile, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"Error for level {level}: {stderr.decode()}")
                else:
                    print(f"Analysis for level {level} completed successfully.")

        except Exception as e:
            print(f"Error running flawfinder for level {level}: {str(e)}")
            continue

        results = parse_flawfinder_output(output_txt_file)

        for result in results:
            unique_key = (result["file_path"], result["line_number"])
            if unique_key not in unique_results[level]:
                unique_results[level].add(unique_key)
                if f"risk_level_{level}" not in parsed_results:
                    parsed_results[f"risk_level_{level}"] = []
                parsed_results[f"risk_level_{level}"].append(result)

    return parsed_results


def prepare_repository(repo_url=None, zip_file_name=None, token=None):
    repo_name = check_name(repo_url=repo_url, zip_file_name=zip_file_name)
    directory: Final[pathlib.Path] = MAIN_DIR / repo_name
    directory.mkdir(parents=True, exist_ok=True)

    if repo_url:
        print(f"Directory {directory} is empty. Cloning repository...")
        try:
            clone_repo(repo_url, directory, token)
        except RepositoryNotFoundError:
            remove_all_files(directory)
            return
    elif zip_file_name:
        zip_file_path = directory / zip_file_name
        copy_zip_to_directory(zip_file_path, directory)
    else:
        print(f"Directory {directory} is empty.")

    return directory


def main(repo_url=None, zip_file_name=None, json_file=None, verbose=None, output_txt_file=None):
    directory = prepare_repository(repo_url=repo_url, zip_file_name=zip_file_name)

    if directory:
        extract_archives_in(directory)
        result = analyze_file_with_repo_scraper(directory, verbose=verbose, output_txt_file=output_txt_file)
        print(result)
        remove_all_files(directory)

        with json_file.open('w') as outfile:
            json.dump(result, outfile, indent=4)
        print(f"Parsed Results saved to {json_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scan repository or directory for files.')
    parser.add_argument('--repo-url', type=str, help='URL of the git repository.')
    # parser.add_argument('--token', type=str, help='GitHub Personal Access Token for private repositories.')
    parser.add_argument('--input-zip', type=pathlib.Path, help='Path to the input zip.')
    parser.add_argument('--output', type=pathlib.Path, help='Path to save the analysis results in JSON format.')
    parser.add_argument('--verbose', type=int, choices=range(0, 6), default=2, help='Set verbosity level (0-5)')

    args = parser.parse_args()
    MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    JSON_FILE: Final[pathlib.Path] = MAIN_DIR / args.output
    output_txt_file: Final[pathlib.Path] = MAIN_DIR / "output_txt_file.txt"

    time_start = time.time()
    main(repo_url=args.repo_url, zip_file_name=args.input_zip, json_file=JSON_FILE, verbose=args.verbose,
         output_txt_file=output_txt_file)
    print(time.time() - time_start)
