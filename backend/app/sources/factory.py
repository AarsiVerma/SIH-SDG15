"""Video source factory."""
from uuid import UUID

from app.sources.base import VideoSource
from app.sources.file_source import FileVideoSource
from app.sources.webcam_source import WebcamVideoSource
from app.sources.rtsp_source import RTSPVideoSource
from app.models.camera import CameraSource
from app.models.enums import SourceType


def build_source(camera_source: CameraSource) -> VideoSource:
    """Build a VideoSource from a CameraSource database row."""
    if camera_source.source_type == SourceType.FILE:
        return FileVideoSource(
            camera_id=camera_source.camera_id,
            path=camera_source.uri,
            source_id=camera_source.id,
        )
    elif camera_source.source_type == SourceType.WEBCAM:
        # URI is device index as string
        try:
            device_index = int(camera_source.uri)
        except ValueError:
            device_index = 0
        return WebcamVideoSource(
            camera_id=camera_source.camera_id,
            device_index=device_index,
            source_id=camera_source.id,
        )
    elif camera_source.source_type == SourceType.RTSP:
        return RTSPVideoSource(
            camera_id=camera_source.camera_id,
            rtsp_url=camera_source.uri,
            source_id=camera_source.id,
        )
    else:
        raise ValueError(f"Unknown source type: {camera_source.source_type}")