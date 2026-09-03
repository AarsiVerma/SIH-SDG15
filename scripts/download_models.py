#!/usr/bin/env python3
"""Download model weights placeholder — prints where to place ONNX files.

Does NOT download unlicensed weights. YOLOX ONNX can be obtained from
Apache-licensed sources. See docs/THIRD_PARTY_LICENSES.md for license policy.
"""
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print(f"Model directory: {MODELS_DIR}")
print("Expected files (Apache-2.0 licensed):")
print("  - yolox_s.onnx  (YOLOX-S, ~9 MB)")
print("  - yolox_m.onnx  (YOLOX-M, ~25 MB)")
print("  - yolox_l.onnx  (YOLOX-L, ~54 MB)")
print()
print("Download from official YOLOX ONNX export or convert from PyTorch:")
print("  https://github.com/Megvii-BaseDetection/YOLOX")
print()
print("Place .onnx files in:", MODELS_DIR)
print("Set DETECTOR_BACKEND=onnx in .env to enable.")