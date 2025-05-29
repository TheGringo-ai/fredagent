import shutil
import difflib
from datetime import datetime
from pathlib import Path

class PatchAssistant:
    def __init__(self, backup_dir=".backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def backup_file(self, file_path: Path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = self.backup_dir / f"{file_path.name}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        print(f"Backup saved at: {backup_path}")
        return backup_path

    def show_diff(self, old_lines, new_lines):
        diff = difflib.unified_diff(old_lines, new_lines, fromfile='original', tofile='patched')
        print("\n".join(diff))

    def apply_patch(self, file_path: Path, new_content: str):
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return False

        old_lines = file_path.read_text().splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        self.show_diff(old_lines, new_lines)

        confirm = input("Apply this patch? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Patch aborted.")
            return False

        self.backup_file(file_path)
        file_path.write_text(new_content)
        print(f"Patch applied to {file_path}")
        return True

    def patch_summarizer_import(self, file_path: Path):
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        content = file_path.read_text()
        new_import = "from web.memory.summarizer_engine import Summarizer"
        if "from web.memory.summarizer import Summarizer" not in content:
            print("⚠️ No matching import line to patch.")
            return False

        updated_content = content.replace("from web.memory.summarizer import Summarizer", new_import)
        return self.apply_patch(file_path, updated_content)


if __name__ == "__main__":
    assistant = PatchAssistant()
    file_to_patch = Path(input("Path to file to patch: ").strip())
    print(f"📄 Selected file: {file_to_patch}")
    assistant.patch_summarizer_import(file_to_patch)