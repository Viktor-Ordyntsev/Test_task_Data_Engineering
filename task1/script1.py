from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

FIGURE_TAGS = {"box", "polygon", "points"}


def collect_image_records(xml_files: List[Path]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for xml_path in xml_files:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for image in root.findall(".//image"):
            width = int(image.get("width", 0))
            height = int(image.get("height", 0))
            name = image.get("name", "")

            figure_count = sum(1 for child in image if child.tag in FIGURE_TAGS)
            records.append(
                {
                    "source_file": xml_path.name,
                    "name": Path(name).name or "<without_name>",
                    "width": width,
                    "height": height,
                    "area": width * height,
                    "figure_count": figure_count,
                }
            )

    return records


def build_report(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "Не найдено изображений для обработки."

    total_images = len(records)
    annotated = sum(1 for record in records if record["figure_count"] > 0)
    unannotated = total_images - annotated
    total_figures = sum(record["figure_count"] for record in records)

    max_area = max(record["area"] for record in records)
    min_area = min(record["area"] for record in records)

    largest = [record for record in records if record["area"] == max_area]
    smallest = [record for record in records if record["area"] == min_area]

    largest_sample = largest[0]
    smallest_sample = smallest[0]

    lines = [
        "Общая статистика",
        f"1. Общее количество изображений: {total_images}",
        f"2. Количество размеченных изображений: {annotated}",
        f"3. Количество неразмеченных изображений: {unannotated}",
        f"4. Количество фигур: {total_figures}",
        (
            f"5. Самое большое изображение: {largest_sample['name']} "
            f"(ширина={largest_sample['width']}, высота={largest_sample['height']}, "
            f"количество={len(largest)})"
        ),
        (
            f"6. Самое маленькое изображение: {smallest_sample['name']} "
            f"(ширина={smallest_sample['width']}, высота={smallest_sample['height']}, "
            f"количество={len(smallest)})"
        ),
    ]
    return "\n".join(lines)


def save_report(report: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Собирает статистику по XML-аннотациям")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "input_data",
        help="Папка с XML-файлами (по умолчанию: task1/input_data)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Опциональный путь к txt-файлу для сохранения отчёта",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_dir}")

    xml_files = sorted(input_dir.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"В папке {input_dir} не найдено XML-файлов")

    records = collect_image_records(xml_files)
    report = build_report(records)

    print(report)

    if args.output:
        save_report(report, args.output)
        print(f"\nОтчёт сохранён в {args.output}")


if __name__ == "__main__":
    main()
