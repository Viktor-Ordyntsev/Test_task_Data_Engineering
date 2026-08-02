from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_coco_data(annotation_path: Path) -> Dict[str, Any]:
    with annotation_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_dataset(annotation_path: Path, output_dir: Path) -> Dict[str, Any]:
    coco_data = load_coco_data(annotation_path)

    images = coco_data.get("images", [])
    annotations = coco_data.get("annotations", [])
    categories = coco_data.get("categories", [])

    image_ids = {image["id"] for image in images}
    category_ids = {category["id"] for category in categories}

    errors: List[Dict[str, Any]] = []
    missing_files = 0
    empty_images = 0

    for image in images:
        file_name = image.get("file_name", "")
        image_path = output_dir / file_name
        if not image_path.exists():
            missing_files += 1
            errors.append(
                {
                    "type": "missing_file",
                    "image_id": image.get("id"),
                    "file_name": file_name,
                }
            )

        if not any(annotation.get("image_id") == image.get("id") for annotation in annotations):
            empty_images += 1

    for annotation in annotations:
        if annotation.get("image_id") not in image_ids:
            errors.append(
                {
                    "type": "missing_image_id",
                    "annotation_id": annotation.get("id"),
                    "image_id": annotation.get("image_id"),
                }
            )

        if annotation.get("category_id") not in category_ids:
            errors.append(
                {
                    "type": "missing_category_id",
                    "annotation_id": annotation.get("id"),
                    "category_id": annotation.get("category_id"),
                }
            )

    report = {
        "images_count": len(images),
        "annotations_count": len(annotations),
        "categories_count": len(categories),
        "empty_images_count": empty_images,
        "missing_files_count": missing_files,
        "errors_count": len(errors),
        "errors": errors,
    }
    return report


def save_report(report: Dict[str, Any], output_path: Path, format_name: str = "json") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format_name == "md":
        lines = [
            "# Dataset validation report",
            "",
            f"- Images: {report['images_count']}",
            f"- Annotations: {report['annotations_count']}",
            f"- Categories: {report['categories_count']}",
            f"- Empty images: {report['empty_images_count']}",
            f"- Missing files: {report['missing_files_count']}",
            f"- Errors: {report['errors_count']}",
            "",
            "## Errors",
        ]
        if report["errors"]:
            for error in report["errors"]:
                lines.append(f"- {error['type']}: {error}")
        else:
            lines.append("- No errors found")
        output_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Валидация COCO-датасета")
    parser.add_argument(
        "--annotation",
        type=Path,
        default=Path(__file__).resolve().parent / "updated_data" / "updated_annotations.json",
        help="Путь к обновлённому COCO JSON",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parent / "updated_data",
        help="Корень датасета с изображениями и аннотациями",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "updated_data" / "dataset_report.json",
        help="Путь к файлу отчёта",
    )
    parser.add_argument(
        "--format",
        choices=["json", "md"],
        default="json",
        help="Формат отчёта: json или md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    annotation_path = args.annotation.resolve()
    data_root = args.data_root.resolve()
    output_path = args.output.resolve()

    if not annotation_path.exists():
        raise FileNotFoundError(f"Аннотации не найдены: {annotation_path}")

    report = validate_dataset(annotation_path, data_root)
    save_report(report, output_path, format_name=args.format)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nОтчёт сохранён в {output_path}")


if __name__ == "__main__":
    main()
