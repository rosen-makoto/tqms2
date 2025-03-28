import os
from pathlib import Path
import gitignore_parser
import mimetypes
import sys # To get the script's own name

# --- Configuration ---
OUTPUT_FILENAME = "combined_code.txt" # Name of the output file
START_DIR = "."                     # Directory to start scanning ('.' means current dir)

# --- Filtering Options ---
USE_GITIGNORE = True          # Set to True to respect .gitignore files
GITIGNORE_PATH = ".gitignore" # Path to the main .gitignore file (relative to START_DIR)

# --- File/Directory Skipping ---
# Specific file exclusions
SKIP_SELF_SCRIPT = True       # Exclude this script file itself?
SKIP_OUTPUT_FILE = True       # Exclude the generated output file?
SKIP_GITIGNORE_FILE = True    # Exclude the .gitignore file specified in GITIGNORE_PATH?

# Django specific exclusions
IGNORE_DJANGO_MIGRATIONS = True # Set to True to ignore 'migrations' folders
IGNORE_DJANGO_STATIC = True     # Set to True to ignore 'static' and 'staticfiles' folders
DJANGO_MIGRATIONS_DIR_NAME = "migrations"
DJANGO_STATIC_DIRS_NAMES = ["static", "staticfiles"]

# General directory/file patterns to ignore
ALWAYS_IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".vscode", ".idea", "build", "dist", "media"}
ALWAYS_IGNORE_FILES = {'.DS_Store'}

# Binary file handling
SKIP_BINARY_FILES = True      # Attempt to skip binary files
MAX_BINARY_CHECK_BYTES = 1024 # Read first N bytes to check for null byte
# --- End Configuration ---

# --- Get Script Filename ---
# Best effort to get the name of the script being run
try:
    # __file__ exists when run as a script
    SCRIPT_FILENAME = Path(__file__).name
except NameError:
    # Fallback if __file__ is not defined (e.g., interactive session, freezing)
    SCRIPT_FILENAME = None
    print("WARNING: Could not determine script filename automatically.")
# --- End Script Filename ---


def is_likely_binary(file_path: Path) -> bool:
    """Tries to guess if a file is binary by checking for null bytes or decoding errors."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(MAX_BINARY_CHECK_BYTES)
        if not chunk: # Handle empty files - treat as text
             return False
        if b'\0' in chunk:
            return True
        try:
            chunk.decode('utf-8')
        except UnicodeDecodeError:
            return True # Failed to decode as UTF-8, likely binary
    except IOError:
        return True
    except Exception:
         return True
    return False

def should_ignore_dir(dir_name: str, dir_path: Path, base_path: Path) -> bool:
    """Checks if a directory name or path should be ignored based on rules."""
    dir_name_lower = dir_name.lower()
    if dir_name in ALWAYS_IGNORE_DIRS:
        return True

    relative_path = dir_path.relative_to(base_path) # Keep for potential future rules
    if IGNORE_DJANGO_MIGRATIONS and dir_name_lower == DJANGO_MIGRATIONS_DIR_NAME:
        return True
    if IGNORE_DJANGO_STATIC and dir_name_lower in DJANGO_STATIC_DIRS_NAMES:
        return True
    return False

def should_ignore_file(file_name: str, file_path: Path, base_path: Path, output_path: Path, gitignore_path_obj: Path) -> bool:
    """Checks if a file name or path should be ignored based on various rules."""
    # 1. Specific file exclusions (Script, Output, .gitignore)
    if SKIP_SELF_SCRIPT and SCRIPT_FILENAME and file_name == SCRIPT_FILENAME:
        print(f"Skipping file (Self): {file_path.relative_to(base_path)}")
        return True
    if SKIP_OUTPUT_FILE and file_path == output_path:
        # This check might be redundant if output is in an ignored dir, but good practice
        print(f"Skipping file (Output): {file_path.relative_to(base_path)}")
        return True
    if SKIP_GITIGNORE_FILE and file_path == gitignore_path_obj:
        print(f"Skipping file (.gitignore): {file_path.relative_to(base_path)}")
        return True

    # 2. Always ignore list
    if file_name in ALWAYS_IGNORE_FILES:
        print(f"Skipping file (Always Ignore Rule): {file_path.relative_to(base_path)}")
        return True

    # 3. Django rules (check parent directory parts)
    try:
        relative_path = file_path.relative_to(base_path)
        parent_parts = relative_path.parent.parts
        if IGNORE_DJANGO_MIGRATIONS and DJANGO_MIGRATIONS_DIR_NAME in parent_parts:
            print(f"Skipping file (Django Migrations Dir): {relative_path}")
            return True
        if IGNORE_DJANGO_STATIC and any(p in parent_parts for p in DJANGO_STATIC_DIRS_NAMES):
            print(f"Skipping file (Django Static Dir): {relative_path}")
            return True
    except ValueError: # Should not happen if file_path is under base_path
        pass

    # 4. Binary file check
    if SKIP_BINARY_FILES and is_likely_binary(file_path):
        print(f"Skipping file (Binary?): {file_path.relative_to(base_path)}")
        return True

    # If none of the above rules match, don't ignore based on these checks
    return False


def combine_code_from_walk(start_dir: str, output_filename: str):
    """
    Walks the directory tree, applying ignore rules, and concatenates allowed files.
    """
    base_path = Path(start_dir).resolve()
    output_path = base_path / output_filename
    # Resolve the gitignore path object for direct comparison later
    gitignore_path_obj = (base_path / GITIGNORE_PATH).resolve()

    print(f"Starting directory scan from: {base_path}")
    print(f"Output will be saved to: {output_path}")
    if SCRIPT_FILENAME:
        print(f"Script filename detected as: {SCRIPT_FILENAME}")

    # --- Load .gitignore ---
    ignore_matches = None
    if USE_GITIGNORE:
        # Use the resolved gitignore_path_obj here
        if gitignore_path_obj.is_file():
            try:
                print(f"Loading .gitignore rules from: {gitignore_path_obj}")
                with open(gitignore_path_obj, 'r', encoding='utf-8') as f_ignore:
                    ignore_matches = gitignore_parser.parse(f_ignore)
                print(".gitignore rules loaded successfully.")
            except Exception as e:
                print(f"WARNING: Could not read or parse {gitignore_path_obj}: {e}")
        else:
            # Check if the non-resolved path exists either, just for informative message
            if not (Path(start_dir) / GITIGNORE_PATH).exists():
                 print(f"INFO: .gitignore file not found at {gitignore_path_obj}. Skipping .gitignore checks.")
            else:
                 print(f"INFO: .gitignore found at relative path but resolved path {gitignore_path_obj} seems incorrect or inaccessible.")


    processed_files_count = 0
    skipped_files_count = 0
    skipped_dirs_count = 0

    try:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for dirpath, dirnames, filenames in os.walk(base_path, topdown=True):
                current_dir_path = Path(dirpath)
                relative_dir_path = current_dir_path.relative_to(base_path)

                # --- Prune Ignored Directories ---
                dirs_to_remove = set()
                for dir_name in dirnames: # No need for index/pop, just rebuild the list
                    dir_full_path = current_dir_path / dir_name
                    should_skip = False
                    reason = ""

                    if should_ignore_dir(dir_name, dir_full_path, base_path):
                        should_skip = True
                        reason = "Rule"
                    elif ignore_matches and ignore_matches(dir_full_path):
                         # Check .gitignore only if not already skipped by rule
                         should_skip = True
                         reason = ".gitignore"

                    if should_skip:
                        print(f"Skipping directory ({reason}): {relative_dir_path / dir_name}")
                        dirs_to_remove.add(dir_name)
                        skipped_dirs_count += 1

                # Modify dirnames *in-place* for os.walk pruning
                dirnames[:] = [d for d in dirnames if d not in dirs_to_remove]


                # --- Process Files in the Current Directory ---
                for filename in filenames:
                    file_full_path = current_dir_path / filename
                    relative_file_path = file_full_path.relative_to(base_path)

                    should_skip_file = False
                    skip_reason = ""

                    # 1. Check specific exclusions, always ignore list, Django structure, binary files
                    if should_ignore_file(filename, file_full_path, base_path, output_path, gitignore_path_obj):
                        should_skip_file = True
                        # Skip reason is printed inside should_ignore_file for these rules

                    # 2. Check .gitignore (only if not already skipped by other rules)
                    elif ignore_matches and ignore_matches(file_full_path):
                         should_skip_file = True
                         skip_reason = ".gitignore" # Need to print reason here

                    if should_skip_file:
                        if skip_reason: # Print reason only if it wasn't printed inside should_ignore_file
                            print(f"Skipping file ({skip_reason}): {relative_file_path}")
                        skipped_files_count += 1
                        continue

                    # --- If file is not skipped, process it ---
                    print(f"Processing: {relative_file_path}")
                    processed_files_count += 1
                    try:
                        with open(file_full_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                            content = f_in.read()
                        f_out.write(f"--- START FILE: {relative_file_path} ---\n\n")
                        f_out.write(content)
                        f_out.write(f"\n\n--- END FILE: {relative_file_path} ---\n\n\n")

                    except Exception as e:
                        print(f"ERROR: Could not read file {relative_file_path}: {e}")
                        skipped_files_count += 1
                        f_out.write(f"--- START FILE: {relative_file_path} ---\n\n")
                        f_out.write(f"!!! FAILED TO READ FILE: {e} !!!")
                        f_out.write(f"\n\n--- END FILE: {relative_file_path} ---\n\n\n")


        print(f"\n--- Summary ---")
        print(f"Processed: {processed_files_count} files.")
        print(f"Skipped:   {skipped_files_count} files.")
        print(f"Skipped:   {skipped_dirs_count} directories (and their contents).")
        print(f"Combined content saved to: {output_path}")

    except IOError as e:
        print(f"ERROR: Could not write to output file {output_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during traversal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        import gitignore_parser
    except ImportError:
        print("ERROR: The 'gitignore-parser' library is required.")
        print("Please install it using: pip install gitignore-parser")
        sys.exit(1) # Use sys.exit

    combine_code_from_walk(START_DIR, OUTPUT_FILENAME)