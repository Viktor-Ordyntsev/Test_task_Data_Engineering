from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def load_coco_data(annotation_path: Path) -> Dict[str, object]:
    with annotation_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_category_lookup(coco_data: Dict[str, object]) -> Dict[int, str]:
    categories = coco_data.get("categories", [])
    return {category["id"]: category["name"] for category in categories}


def get_image_classes(image_id: int, annotations: List[Dict[str, object]], category_lookup: Dict[int, str]) -> List[str]:
    classes = []
    for annotation in annotations:
        if annotation.get("image_id") == image_id:
            category_name = category_lookup.get(annotation.get("category_id"))
            if category_name and category_name not in classes:
                classes.append(category_name)
    return classes


def normalize_class_name(class_name: str) -> str:
    return re.sub(r"_\d+$", "", class_name).strip()


def build_destination_folder(image_classes: List[str]) -> str:
    if not image_classes:
        return "unknown"
    normalized_classes = [normalize_class_name(name) for name in image_classes]
    return "_".join(sorted(dict.fromkeys(normalized_classes)))


def reconstruct_input_paths(input_dir: Path) -> Tuple[Path, Path]:
    candidates = [
        input_dir,
        input_dir / "extracted",
    ]

    for candidate in candidates:
        annotation_path = candidate / "annotations" / "instances_train.json"
        images_root = candidate / "images" / "train"
        if annotation_path.exists() and images_root.exists():
            return annotation_path, images_root

    raise FileNotFoundError(f"Не удалось найти датасет в папке: {input_dir}")


def restructure_dataset(input_dir: Path, output_dir: Path) -> Tuple[List[Path], Path]:
    annotation_path, images_root = reconstruct_input_paths(input_dir)

    coco_data = load_coco_data(annotation_path)
    category_lookup = build_category_lookup(coco_data)

    annotations = coco_data.get("annotations", [])
    images = coco_data.get("images", [])

    output_images_root = output_dir / "images"
    output_images_root.mkdir(parents=True, exist_ok=True)

    updated_images = []
    for image_info in images:
        image_id = image_info["id"]
        source_path = images_root / image_info["file_name"]
        if not source_path.exists():
            continue

        image_classes = get_image_classes(image_id, annotations, category_lookup)
        destination_folder = output_images_root / build_destination_folder(image_classes)
        destination_folder.mkdir(parents=True, exist_ok=True)

        destination_path = destination_folder / image_info["file_name"]
        shutil.copy2(source_path, destination_path)

        updated_image = dict(image_info)
        relative_path = destination_path.relative_to(output_dir)
        updated_image["file_name"] = str(relative_path).replace("\\", "/")
        updated_images.append(updated_image)

    updated_annotations = dict(coco_data)
    updated_annotations["images"] = updated_images

    updated_annotation_path = output_dir / "updated_annotations.json"
    with updated_annotation_path.open("w", encoding="utf-8") as fh:
        json.dump(updated_annotations, fh, indent=2, ensure_ascii=False)

    return sorted(output_images_root.rglob("*")), updated_annotation_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Реструктуризация COCO-датасета по классам")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "input_data",
        help="Папка с распакованным датасетом (по умолчанию: task2/input_data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "updated_data",
        help="Папка для сохранения обновлённой структуры и аннотаций",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_dir}")

    output_files, updated_annotation_path = restructure_dataset(input_dir, output_dir)

    print(f"Создано файлов: {len(output_files)}")
    print(f"Обновлённые аннотации: {updated_annotation_path}")


if __name__ == "__main__":
    main()
