# VANRAKSHA AI — Limitations & Honest Disclaimers

## What This System Does

- Detects objects (person, vehicle, animal, fire, smoke) in video files
- Tracks objects across frames with stable IDs (per camera)
- Correlates multi-signal events (person + vehicle + restricted zone + night)
- Computes deterministic, explainable risk scores with factor breakdown
- Creates and manages incidents with evidence, status workflow, audit trail
- Provides Command Centre UI with map, real-time updates, evidence viewer
- Supports offline edge collection with later sync

## What This System Does NOT Do

| Capability | Status | Notes |
|------------|--------|-------|
| **Identify specific individuals** | ❌ | No face recognition, no ReID across cameras |
| **Classify animal species** | ❌ | All animals = "unknown"; MegaDetector optional ADVANCED |
| **Predict fire spread** | ❌ | `spread_prediction: null` always in MVP |
| **Legally admissible evidence** | ❌ | SHA-256 + timestamp only; no chain-of-custody, no notarization |
| **Auto-close incidents** | ❌ | Only human can CLOSE; AI never auto-resolves |
| **Cross-camera tracking** | ❌ | Track IDs are per-camera, per-job |
| **Real-time streaming from RTSP** | ⚠️ | Supported but untested; MVP uses file sources |
| **Mobile app for rangers** | ❌ | Simulated GPS/SOS only |
| **Predictive poaching hotspots** | ❌ | No ML risk model; deterministic rules only |
| **Weapon detection** | ❌ | No reliable class in COCO/YOLOX |
| **Audio analysis** | ❌ | Video only |
| **Satellite / drone integration** | ❌ | Protocols defined (VR-096), not implemented |

## Model Limitations

- **Detector**: YOLOX (COCO classes) or DummyDetector. COCO has 80 classes; mapped to 6 taxonomy classes.
- **Classes ignored**: bicycle, backpack, bottle, chair, etc. mapped to `unknown` or dropped.
- **Fire/smoke**: Only if custom model provides these classes; standard YOLOX does not have them.
- **Tracker**: ByteTrack (MIT) or IoU fallback. No ReID, no cross-camera association.
- **Confidence thresholds**: Fixed at 0.25 (detector), 0.5 (tracker). Not configurable per-class.

## Geospatial Limitations

- **Camera location ≠ object location**: Object GPS estimated from camera point only (no homography).
- **Zone membership**: Based on camera point, not object position.
- **Ranger proximity**: Based on camera point, not object position.
- **No 3D/terrain**: All calculations on WGS84 ellipsoid.
- **CRS**: EPSG:4326 only.

## Risk Engine Limitations

- **Deterministic rules only**: No ML, no learning from outcomes (outcomes recorded for future).
- **Factor weights**: Configurable but default values are placeholders.
- **No temporal patterns beyond "repeated movement"**: No behavior modeling.
- **Negative factors**: Only "authorized_ranger" implemented.
- **Threshold for incident**: `incident_min_level` (default MEDIUM) — not per-event-type.

## Evidence Limitations

- **JPEG only**: No video clips in MVP.
- **Storage**: Local filesystem with SHA-256. No cloud, no signed URLs.
- **Disclaimer**: "Timestamped evidence supporting investigation, subject to applicable procedures."
- **No chain of custody**: No tamper-evident logs beyond audit trail.

## Operational Limitations

- **Single-node only**: No HA, no horizontal scaling.
- **In-memory rate limiter**: Resets on restart; not distributed.
- **In-process job queue**: No Celery/Redis; jobs run in worker process.
- **No backup/restore automation**: `pg_dump` script provided, manual.
- **Demo passwords**: `changeme` — must override in production.
- **Timezone**: Fixed to Asia/Kolkata (configurable but not per-user).

## Data Quality

- **DummyDetector**: Deterministic scripted boxes — not real detections.
- **Synthetic timestamps**: Frame timestamps = start_time + seq/fps.
- **No real animal behavior**: Wildlife anomaly heuristics are toy examples.
- **No night vision simulation**: Day/night based on clock only.

## Legal & Compliance

- **Not a law enforcement tool**: Outputs are "investigation support," not evidence.
- **No facial recognition**: Explicitly excluded.
- **No biometric processing**: GDPR/PDPA considerations apply if deployed.
- **Audit logs**: Best-effort; not tamper-proof (standard DB).
- **License**: Apache-2.0 for code; third-party licenses vary (see THIRD_PARTY_LICENSES.md).

## Performance Targets (MVP)

| Metric | Target |
|--------|--------|
| FPS (640px, CPU) | 2 FPS sustained |
| Detection latency | < 500ms/frame |
| Event → Incident | < 1s |
| WebSocket latency | < 100ms LAN |
| DB size (1yr, 10 cams) | ~50 GB |

## Future Work (See FUTURE.md)

- Species classification (MegaDetector)
- Fire spread physics (Rothermel)
- Cross-camera ReID
- ML risk model (from outcomes)
- Mobile app (React Native)
- Hardware adapters (IoT, drone, wearable)
- Federated learning across reserves