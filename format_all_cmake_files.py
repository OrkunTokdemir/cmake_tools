import subprocess
import os
import sys
import getopt

def apply_command_to_files(dir_path, file_extensions, file_names, command, skip_dirs, verbose=False):
    """
    Find all files in the specified directory and its subdirectories that match the specified file extensions
    and run command on them, skipping any directories in the skip_dirs list.
    """
    for entry in os.scandir(dir_path):
        if entry.is_file() and (entry.name.endswith(file_extensions) or entry.name in file_names):
            file_path = os.path.relpath(entry.path)
            if verbose:
                print(f"running: {' '.join(command)} {file_path}")

            try:
                subprocess.run(command + [file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error formatting file: {e}")
        elif entry.is_dir() and entry.name.lower() not in skip_dirs:
            apply_command_to_files(entry.path, file_extensions, file_names, command, skip_dirs)

def check_programs(programs):
    """
    Check if the specified programs are installed on the system.
    """
    for program in programs:
        try:
            # run the program without output
            subprocess.run([program, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            # subprocess.run([program, "--version"], check=True)
            return True
        except Exception as e:
            print(f"Error: {e} {program} is not installed. Trying to install it by using pip...")
            try:
                subprocess.run(["pip", "install", program], check=True)
                return True
            except Exception as e:
                print(f"Error: {e} {program} could not be installed. Please install it manually.")
                return False

def check_config_files(files):
    # Check if any of the config files with extensions are in the current directory

    for file in files:
        if os.path.isfile(file):
            return True

    print("No config file found. Trying to dump the default config file...")
    try:
        dump_default_config_file()
        return True
    except Exception as e:
        print(f"Error: {e} Default config file could not be dumped. Please create one manually.")
        return False

def dump_default_config_file():
    print(f"cwd: {os.getcwd()}")
    # write the output to .cmake-format.py file
    subprocess.run(["cmake-format", "--dump-config"], stdout=open(".cmake-format.py", "w"), check=True)
    

def main(args):
    verbose = False
    try: 
        opts, args = getopt.getopt(args, "hv", ["help", "verbose"])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print("Usage: format_all_cmake_files.py [-h] [-v]")
                sys.exit(1)
            elif opt in ("-v", "--verbose"):
                verbose = True
    except getopt.GetoptError:
        print("Usage: format_all_cmake_files.py [-h] [-v]")
        sys.exit(1)
    DIR_PATH = os.getcwd()
    FILE_EXTENSIONS = (".cmake")
    FILE_NAMES = ("CMakeLists.txt")
    SKIP_DIRS = ("build", "bin", "out")
    COMMAND = ["cmake-format", "-i"]
    PROGRAMS_NEEDED = ["cmake-format"]
    CONFIG_FILES = [".cmake-format.py", ".cmake-format.yaml", ".cmake-format.yml"]

    if not check_programs(PROGRAMS_NEEDED):
        print("Please install the yecessary programs and try again.")
        sys.exit(1)
    
    if not check_config_files(CONFIG_FILES):
        print("No config file found. Please create one and try again.")
        sys.exit(1)

    apply_command_to_files(DIR_PATH, FILE_EXTENSIONS, FILE_NAMES, COMMAND, SKIP_DIRS, verbose)


if __name__ == "__main__":
    # call main with cli arguments
    main(sys.argv[1:])
