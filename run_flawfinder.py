import argparse
import pathlib
import subprocess
import time
from typing import Final

from Run_modules.result_saver import parse_flawfinder_output
from Run_modules.run_modules import check_name, clone_repo, RepositoryNotFoundError, remove_all_files, \
    copy_zip_to_directory, extract_archives_in


def analyze_file_with_repo_scraper(file_path: pathlib.Path, output_txt_file: pathlib.Path, verbose=5, ):
    command = ['python3', 'flawfinder', '--minlevel', verbose, str(file_path), '>', str(output_txt_file)]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode()
    except Exception as e:
        return f"Error running repo-scraper: {str(e)}"


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
        analyze_file_with_repo_scraper(directory, verbose=verbose, output_txt_file=output_txt_file)
        remove_all_files(directory)

        parse_flawfinder_output(output_file=json_file, input_file=output_txt_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scan repository or directory for files.')
    parser.add_argument('--repo-url', type=str, help='URL of the git repository.')
    # parser.add_argument('--token', type=str, help='GitHub Personal Access Token for private repositories.')
    parser.add_argument('--input-zip', type=pathlib.Path, help='Path to the input zip.')
    parser.add_argument('--output', type=pathlib.Path, help='Path to save the analysis results in JSON format.')
    parser.add_argument('--verbose', type=int, choices=range(0, 6), default=5, help='Set verbosity level (0-5)')

    args = parser.parse_args()
    MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    JSON_FILE: Final[pathlib.Path] = MAIN_DIR / args.output
    output_txt_file: Final[pathlib.Path] = MAIN_DIR / "output_txt_file.txt"

    time_start = time.time()
    main(repo_url=args.repo_url, zip_file_name=args.input_zip, json_file=JSON_FILE, verbose=args.verbose,
         output_txt_file=output_txt_file)
    print(time.time() - time_start)
