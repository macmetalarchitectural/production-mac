import sys
import re
from utils import is_e3k_module

# Liste des champs autorisés sans préfixe e3k_
ALLOWED_FIELDS_WITHOUT_PREFIX = {
    'name',
    'display_name',
    'create_date',
    'write_date',
    'active',
    'state',
}

def is_model_inherited(lines):
    return any(re.search(r"_inherit\s*=\s*['\"]", line) for line in lines)

def check_field_prefix(file_path):
    errors = []

    if not is_e3k_module(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not is_model_inherited(lines):
        return []

    for i, line in enumerate(lines):
        if "# no-check" in line:
            continue

        match = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*fields\.([A-Z][a-zA-Z0-9_]*)\s*\((?!\s*\))", line)
        if match:
            field_name = match.group(1)
            if field_name.startswith("_"):
                continue  # ignorer champs internes
            if field_name in ALLOWED_FIELDS_WITHOUT_PREFIX:
                continue  # ignorer champs autorisés
            if not field_name.lower().startswith("e3k_"):
                errors.append(
                    f"{file_path}:{i+1} - Champ '{field_name}' doit commencer par 'e3k_' (ou ajouter # no-check)"
                )

    return errors

def main():
    failed = False
    for file in sys.argv[1:]:
        if file.endswith(".py"):
            errs = check_field_prefix(file)
            if errs:
                for err in errs:
                    print(err)
                failed = True
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
