from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List

FIGURE_TAGS = {"box", "polygon", "points"}


def collect_shape_type_counts(xml_files: List[Path]) -> Counter:
    shape_type_counts: Counter = Counter()

    for xml_path in xml_files:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for image in root.findall(".//image"):
            for child in image:
                if child.tag in FIGURE_TAGS:
                    shape_type_counts[child.tag] += 1

    return shape_type_counts


def build_report(shape_type_counts: Counter) -> str:
    if not shape_type_counts:
        return "Не найдено фигур в аннотациях."

    lines = ["Статистика по типам фигур"]
    for shape_type in ["box", "polygon", "points"]:
        count = shape_type_counts.get(shape_type, 0)
        lines.append(f"{shape_type}: {count}")
    return "\n".join(lines)


def save_report(report: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Считает количество фигур по типам")
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

    shape_type_counts = collect_shape_type_counts(xml_files)
    report = build_report(shape_type_counts)

    print(report)

    if args.output:
        save_report(report, args.output)
        print(f"\nОтчёт сохранён в {args.output}")


if __name__ == "__main__":
    main()
