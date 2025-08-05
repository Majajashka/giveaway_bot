import os
import re
import logging

logger = logging.getLogger(__name__)

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',     # Синий
        'INFO': '\033[92m',      # Зелёный
        'WARNING': '\033[93m',   # Жёлтый
        'ERROR': '\033[91m',     # Красный
        'CRITICAL': '\033[1;91m' # Ярко-красный
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

def setup_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def replace_in_imports(filepath, old_text, new_text):
    changed = False
    pattern_import = re.compile(rf"^(from|import) {re.escape(old_text)}(\.|$)")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if pattern_import.match(line):
            new_line = line.replace(old_text, new_text)
            if new_line != line:
                changed = True
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        logger.info(f"Импорты изменены в {filepath}")

def replace_in_pyproject(filepath, old_text, new_text):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_text in content:
        content_new = content.replace(old_text, new_text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_new)
        logger.info(f"Заменено в {filepath}")


def replace_in_dockerfile(filepath, old_text, new_text):
    changed = False
    new_lines = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # Заменяем только в строках, где явно может использоваться имя директории или модуля
        if any(cmd in line for cmd in ['COPY', 'ADD', 'RUN', 'CMD', 'WORKDIR']):
            new_line = line.replace(old_text, new_text)
            if new_line != line:
                changed = True
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        logger.info(f"Заменено в Dockerfile: {filepath}")


def main(root_dir, old_text, new_text):
    logger.info(f"Начинаем замену '{old_text}' на '{new_text}'")
    changed_files = 0

    for root, dirs, files in os.walk(root_dir):
        if ".venv" in dirs:
            dirs.remove(".venv")

        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.py'):
                replace_in_imports(filepath, old_text, new_text)
                changed_files += 1
            elif file in ('pyproject.toml', 'README.md'):
                replace_in_pyproject(filepath, old_text, new_text)
                changed_files += 1
            elif file == 'Dockerfile':
                replace_in_dockerfile(filepath, old_text, new_text)
                changed_files += 1

    old_folder = os.path.join(root_dir, 'src', old_text)
    new_folder = os.path.join(root_dir, 'src', new_text)
    if os.path.exists(old_folder):
        os.rename(old_folder, new_folder)
        logger.info(f"Папка {old_folder} переименована в {new_folder}")
    else:
        logger.warning(f"Папка {old_folder} не найдена, переименование пропущено")

    logger.info(f"Обработано файлов: {changed_files}")
    logger.info("Готово!")

if __name__ == "__main__":
    setup_logger()
    root_directory = "./"
    old_str = "template"
    new_str = "giveaway_bot"
    main(root_directory, old_str, new_str)
