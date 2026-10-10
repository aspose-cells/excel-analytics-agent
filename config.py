import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL", "gpt-oss")
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = PROJECT_ROOT / "samples"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Aspose.Cells license ¡ª set ASPOSE_LICENSE in .env to a license file path
_license_path = os.getenv("ASPOSE_LICENSE")
if _license_path:
    try:
        import aspose.cells
        aspose.cells.License().set_license(_license_path)
    except Exception:
        pass