import os
import re

# Directory containing the Flutter code
FLUTTER_DIR = "lib"

# Import statement for `app_strings.dart`
APP_STRINGS_IMPORT_STATEMENT = "import 'package:com.floridainc.dosparkles/app_strings.dart';"

# File containing the string constants
APP_STRINGS_FILE = os.path.join(FLUTTER_DIR, "app_strings.dart")

# Pattern to match string constants
CONSTANT_PATTERN = r'  static const String (\w+) = "([^"]+)";'

# Load all constants from `app_strings.dart`
constants = {}
if os.path.exists(APP_STRINGS_FILE):
    with open(APP_STRINGS_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(CONSTANT_PATTERN, line)
            if match:
                constants[match.group(2)] = match.group(1)

# Regex pattern to match quoted strings (including multiline)
QUOTE_PATTERN = re.compile(r"([\'\"])(.*?)(\1)", re.DOTALL)
SNAKEBAR_MSG_PATTERN = r'msg\s*:\s*([\'\"])(.*?)(\1)'

# Function to replace hard-coded strings within quotes and custom patterns
def replace_hardcoded_strings(content, constants):
    modified = False

    def replace_in_quotes(match):
        nonlocal modified
        quote = match.group(1)
        text = match.group(2)
        if text in constants:
            replacement = f'${{AppStrings.{constants[text]}}}'
            modified = True
            return f'{quote}{replacement}{quote}'
        return match.group(0)

    def replace_in_snakebar_msg(match):
        nonlocal modified
        quote = match.group(1)
        text = match.group(2)
        if text in constants:
            replacement = f'${{AppStrings.{constants[text]}}}'
            modified = True
            return f'msg: {quote}{replacement}{quote}'
        return match.group(0)

    # Replace strings inside quotes
    content = QUOTE_PATTERN.sub(replace_in_quotes, content)

    # Replace `msg` parameter in `showColoredSnakeBar`
    content = re.sub(SNAKEBAR_MSG_PATTERN, replace_in_snakebar_msg, content)

    return content, modified

# Function to ensure `app_strings.dart` is imported only if required
def ensure_import(content, import_statement, modified):
    if modified and import_statement not in content:
        content = import_statement + '\n' + content
    return content

# Process all Dart files except excluded ones
EXCLUDED_FILES = {'app_strings.dart', 'firebase_options.dart'}
IGNORED_FOLDERS = {'actions', 'const', 'controllers', 'gen', 'generated', 'globalbasestate', 'l10n', 'models', 'utils', }

for subdir, dirs, files in os.walk(FLUTTER_DIR):
    # Remove ignored folders from the list of subdirectories
    dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

    for file in files:
        if file.endswith(".dart") and file not in EXCLUDED_FILES:
            file_path = os.path.join(subdir, file)
            with open(file_path, "r", encoding="utf-8") as source_file:
                content = source_file.read()

            # Replace hard-coded strings
            updated_content, modified = replace_hardcoded_strings(content, constants)

            # Ensure import only if changes were made
            updated_content = ensure_import(updated_content, APP_STRINGS_IMPORT_STATEMENT, modified)

            # Write back only if changes were made
            if content != updated_content:
                with open(file_path, "w", encoding="utf-8") as target_file:
                    target_file.write(updated_content)

print("All hard-coded strings have been replaced with AppStrings constants.")
