from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List


def modify_xml_files(xml_files: List[Path], output_dir: Path) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_files: List[Path] = []

    for xml_path in xml_files:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        images = root.findall(".//image")
        if not images:
            continue

        image_ids = [image.get("id") for image in images if image.get("id") is not None]
        if len(image_ids) != len(images):
            continue

        reversed_ids = list(reversed(image_ids))
        for image, new_id in zip(images, reversed_ids):
            image.set("id", str(new_id))

        for image in images:
            original_name = image.get("name", "")
            if not original_name:
                continue

            file_name = Path(original_name).name
            stem = Path(file_name).stem
            image.set("name", f"{stem}.png")

        output_path = output_dir / f"{xml_path.stem}_modified.xml"
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        written_files.append(output_path)

    return written_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Модифицирует XML-аннотации и сохраняет копии")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "input_data",
        help="Папка с XML-файлами (по умолчанию: task1/input_data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "modified_output",
        help="Папка для сохранения изменённых XML (по умолчанию: task1/modified_output)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_dir}")

    xml_files = sorted(input_dir.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"В папке {input_dir} не найдено XML-файлов")

    written_files = modify_xml_files(xml_files, output_dir)

    print(f"Создано файлов: {len(written_files)}")
    for path in written_files:
        print(path)


if __name__ == "__main__":
    main()
