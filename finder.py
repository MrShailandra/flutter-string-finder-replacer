import os
import re

# Directory containing the Flutter code
FLUTTER_DIR = "lib"

# Patterns to find hard-coded strings within Text(), hintText, and labelText, and validator returns
TEXT_PATTERN = r'Text\s*\(\s*[\'"]([^\'"$]+)[\'"]\s*(?:,|\))'
HINT_PATTERN = r'hintText\s*:\s*[\'"]([^\'"$]+)[\'"]'
LABEL_PATTERN = r'labelText\s*:\s*[\'"]([^\'"$]+)[\'"]'
VALIDATOR_PATTERN = r'return\s*[\'"]([^\'"$]+)[\'"]'
DIALOG_PATTERN = r'showAlertDialog\s*\(\s*[\'"]([^\'"$]+)[\'"],\s*[\'"]([^\'"$]+)[\'"],.*strCancel\s*:\s*[\'"]([^\'"$]+)[\'"],\s*strSuccess\s*:\s*[\'"]([^\'"]+)[\'"]'
DIALOG_GENERIC_PATTERN = r'showAlertDialog\s*\(\s*[\'"]([^\'"$]+)[\'"],\s*[\'"]([^\'"$]+)[\'"]'
SNAKEBAR_PATTERN = r'showColoredSnakeBar\s*\(.*msg\s*:\s*[\'"]([^\'"]+)[\'"]'
GENERIC_MSG_PATTERN = r'\bmsg\s*:\s*[\'"]([^\'"]+)[\'"]'
COMMENT_PATTERN = r'//.*?$|/\*.*?\*/|\'\'\'.*?\'\'\'|\"\"\".*?\"\"\"'

# File to hold the constants
APP_STRINGS_FILE = os.path.join(FLUTTER_DIR, "app_strings.dart")

# Directories to be ignored
IGNORED_FOLDERS = {'actions', 'const', 'controllers', 'gen', 'generated', 'globalbasestate', 'l10n', 'models', 'utils', }

# Read existing constants
existing_constants = {}
if os.path.exists(APP_STRINGS_FILE):
    with open(APP_STRINGS_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(r'  static const String (\w+) = "([^"]+)";', line)
            if match:
                existing_constants[match.group(2)] = match.group(1)

# Initialize new constants
new_constants = {}

# Reserved keywords in Dart
dart_reserved_keywords = {
    "assert", "break", "case", "catch", "class", "const", "continue", "default", "do",
    "else", "enum", "extends", "false", "final", "finally", "for", "if", "in",
    "new", "null", "rethrow", "return", "super", "switch", "this", "throw", "true",
    "try", "var", "void", "while", "with", "is", "async", "await", "yield",
}

# Mapping digits to words
digit_to_word = {
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
    '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
}

# Helper function to generate valid Dart variable names
def make_constant_name(string, existing):
    constant_name = re.sub(r'[^A-Za-z0-9]+', '_', string).lower()

    # Handle numeric-only names
    if constant_name.isdigit():
        constant_name = '_'.join(digit_to_word[d] for d in constant_name)
    elif constant_name[0].isdigit() or constant_name[0] == '_':
        constant_name = 'dash_' + constant_name

    # Handle reserved keywords
    if constant_name in dart_reserved_keywords:
        constant_name = f'dash_{constant_name}'

    # Make unique if already exists
    original_name = constant_name
    counter = 2
    while constant_name in existing or constant_name in new_constants.values():
        constant_name = f'{original_name}_{counter}'
        counter += 1

    return constant_name

# Process all Dart files
for subdir, dirs, files in os.walk(FLUTTER_DIR):
    # Remove ignored folders from the list of subdirectories
    dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

    for file in files:
        if file.endswith(".dart"):
            file_path = os.path.join(subdir, file)
            with open(file_path, "r", encoding="utf-8") as source_file:
                content = source_file.read()

            # Remove comments to avoid matching strings inside them
            content = re.sub(COMMENT_PATTERN, '', content, flags=re.DOTALL | re.MULTILINE)

            # Find hard-coded strings within Text widgets, hintText, labelText attributes, return statements in validators, showAlertDialog, and showColoredSnakeBar
            text_matches = re.findall(TEXT_PATTERN, content)
            hint_matches = re.findall(HINT_PATTERN, content)
            label_matches = re.findall(LABEL_PATTERN, content)
            validator_matches = re.findall(VALIDATOR_PATTERN, content)
            dialog_matches = [match for group in re.findall(DIALOG_PATTERN, content) for match in group]
            dialog_generic_matches = [match for group in re.findall(DIALOG_GENERIC_PATTERN, content) for match in group]
            snakebar_matches = re.findall(SNAKEBAR_PATTERN, content)
            generic_msg_matches = re.findall(GENERIC_MSG_PATTERN, content)

            all_matches = text_matches + hint_matches + label_matches + validator_matches + dialog_matches + dialog_generic_matches + snakebar_matches + generic_msg_matches

            for string in all_matches:
                if string not in existing_constants and string not in new_constants:
                    constant_name = make_constant_name(string, existing_constants)
                    new_constants[string] = constant_name

# Write new constants to the AppStrings file
with open(APP_STRINGS_FILE, "w", encoding="utf-8") as file:
    file.write('class AppStrings {\n')
    for string, constant in {**existing_constants, **new_constants}.items():
        file.write(f'  static const String {constant} = "{string}";\n')
    file.write('}\n')

# Report newly created constants
print("New constants added to app_strings.dart:")
for string, constant in new_constants.items():
    print(f'{constant}: "{string}"')
