from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_coco_data(annotation_path: Path) -> Dict[str, Any]:
    with annotation_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_class_name(class_name: str) -> str:
    import re

    return re.sub(r"_\d+$", "", class_name).strip()


def convert_to_yolo(annotation_path: Path, data_root: Path, output_dir: Path) -> List[Path]:
    coco_data = load_coco_data(annotation_path)
    categories = coco_data.get("categories", [])
    images = coco_data.get("images", [])
    annotations = coco_data.get("annotations", [])

    category_lookup = {category["id"]: category["name"] for category in categories}
    image_lookup = {image["id"]: image for image in images}

    output_dir.mkdir(parents=True, exist_ok=True)

    created_files: List[Path] = []

    for image in images:
        image_id = image["id"]
        image_file = image.get("file_name", "")
        source_image_path = data_root / image_file
        if not source_image_path.exists():
            continue

        folder_name = Path(image_file).parts[0] if len(Path(image_file).parts) > 1 else "unknown"
        if folder_name == "images":
            rel_parts = Path(image_file).parts[1:]
            folder_name = rel_parts[0] if rel_parts else "unknown"

        class_folder = output_dir / folder_name
        class_folder.mkdir(parents=True, exist_ok=True)

        destination_image = class_folder / Path(image_file).name
        shutil.copy2(source_image_path, destination_image)
        created_files.append(destination_image)

        annotation_lines: List[str] = []
        for annotation in annotations:
            if annotation.get("image_id") != image_id:
                continue

            bbox = annotation.get("bbox", [])
            if len(bbox) != 4:
                continue

            category_id = annotation.get("category_id")
            category_name = category_lookup.get(category_id, "unknown")
            normalized_class = normalize_class_name(category_name)

            x_min, y_min, width, height = bbox
            image_width = image.get("width", 1)
            image_height = image.get("height", 1)

            x_center = (x_min + width / 2) / image_width
            y_center = (y_min + height / 2) / image_height
            bbox_width = width / image_width
            bbox_height = height / image_height

            class_id = None
            for index, cat in enumerate(categories, start=0):
                if cat.get("name") == category_name:
                    class_id = index
                    break

            if class_id is None:
                class_id = 0

            annotation_lines.append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}"
            )

        annotation_path = class_folder / f"{Path(image_file).stem}.txt"
        annotation_path.write_text("\n".join(annotation_lines), encoding="utf-8") if annotation_lines else annotation_path.write_text("", encoding="utf-8")
        created_files.append(annotation_path)

    return created_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Преобразование COCO-аннотаций в YOLO")
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
        help="Корень датасета с изображениями",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "yolo_dataset",
        help="Папка для сохранения YOLO-датасета",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    annotation_path = args.annotation.resolve()
    data_root = args.data_root.resolve()
    output_dir = args.output_dir.resolve()

    if not annotation_path.exists():
        raise FileNotFoundError(f"Аннотации не найдены: {annotation_path}")

    created_files = convert_to_yolo(annotation_path, data_root, output_dir)
    print(f"Создано файлов: {len(created_files)}")
    for path in created_files[:10]:
        print(path)


if __name__ == "__main__":
    main()
