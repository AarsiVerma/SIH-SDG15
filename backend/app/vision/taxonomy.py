"""COCO class ID to Vanraksha taxonomy mapping."""
# COCO classes (80 classes)
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
]

# Map COCO index -> Vanraksha class name
COCO_TO_VR = {
    0: "person",          # person
    1: "vehicle",         # bicycle
    2: "vehicle",         # car
    3: "vehicle",         # motorcycle
    5: "vehicle",         # bus
    7: "vehicle",         # truck
    14: "animal",         # bird
    15: "animal",         # cat
    16: "animal",         # dog
    17: "animal",         # horse
    18: "animal",         # sheep
    19: "animal",         # cow
    20: "animal",         # elephant
    21: "animal",         # bear
    22: "animal",         # zebra
    23: "animal",         # giraffe
    # Note: fire/smoke not in standard COCO - would need custom model
}


def map_class(coco_class_id: int) -> str | None:
    """Map COCO class ID to Vanraksha taxonomy. Returns None for ignored classes."""
    return COCO_TO_VR.get(coco_class_id)


VANRAKSHA_CLASSES = ["person", "vehicle", "animal", "fire", "smoke", "unknown"]
VANRAKSHA_CLASS_IDS = {name: i for i, name in enumerate(VANRAKSHA_CLASSES)}