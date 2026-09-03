# VANRAKSHA AI — Future Work (Post-MVP)

This document captures explicitly deferred work. **None of these are in MVP scope.**

## Hardware Adapters (VR-096 Stubs)

| Source | Protocol | Status |
|--------|----------|--------|
| IoT Sensors (temp, humidity, smoke, AQI, wind) | `SensorSource` | Stubbed in `backend/app/sources/sensor_base.py` |
| Drone telemetry + frames | `DroneSource` | Stubbed in `backend/app/sources/drone_base.py` |
| Satellite imagery | — | Not stubbed |
| Wearable (BLE: HR, fall, GPS) | — | Not stubbed |
| LoRaWAN / Sigfox gateways | — | Not stubbed |

**Integration pattern**: All reuse `Frame` contract → existing detector/tracker pipeline.

## Model Registry & Versioning

```
models/
  registry.json          # {id, version, license, sha256, task, classes, metrics}
  yolox_s.onnx           # v1.0.0, Apache-2.0
  yolox_m.onnx           # v1.0.0
  megadetector_v5a.pt    # v5a, MIT (weights license review needed)
```

- `backend/app/sync/apply.py` should handle model sync to edge
- CI gate: `registry.json` validated against `config/license_policy.yaml`

## Advanced Detection

| Feature | Effort | Dependency |
|---------|--------|------------|
| Species classification (MegaDetector) | Medium | Weights license review, ONNX export |
| Custom fire/smoke model | High | Training data, GPU |
| Thermal/IR camera support | Medium | Different preprocessing |
| Multi-frame detection (temporal) | Medium | Track-aware detection |

## Tracking Enhancements

- **Cross-camera ReID**: OSNet or BoT embeddings + feature gallery
- **Track interpolation**: Kalman smoother for gaps
- **Group tracking**: Cluster nearby same-class tracks
- **Track quality metrics**: Visibility, occlusion, fragmentation

## Geospatial Intelligence

- **Camera calibration**: Homography from 4+ GCPs per camera → object GPS
- **Terrain-aware proximity**: Cost-distance on DEM, not Euclidean
- **Viewshed analysis**: Which zones each camera actually sees
- **Dynamic zone membership**: Object-level, not camera-point

## Risk Engine v2 (ML)

- **Training data**: Incident outcomes (VR-089) → XGBoost/LightGBM
- **Features**: Factor deltas, temporal patterns, spatial clusters, weather
- **Online learning**: Periodic retrain with drift detection
- **Explainability**: SHAP values per factor
- **Calibration**: Platt scaling for probability outputs

## Fire Intelligence

- **Rothermel spread model**: Fuel, slope, wind, weather
- **Satellite hotspot fusion**: FIRMS/VIIRS ingestion
- **Evacuation routing**: Graph on road network + fire perimeter
- **Smoke plume modeling**: HYSPLIT or Gaussian puff

## Wildlife Intelligence

- **Species ID**: MegaDetector + classifier head
- **Migration corridors**: Long-term track aggregation
- **Poaching risk heatmap**: Historical incidents + environmental layers
- **Acoustic monitoring**: Bird/frog calls → biodiversity index

## Ranger Safety

- **Wearable integration**: BLE HR, fall detection, man-down
- **Panic button**: Hardware → SOS event
- **Geofence alerts**: Enter/exit restricted zones
- **Fatigue detection**: HRV + activity patterns

## Command Centre UX

- **3D terrain view**: CesiumJS or MapLibre GL
- **Timeline scrubber**: Replay incidents with tracks
- **Collaborative annotations**: Multi-officer incident notes
- **Mobile PWA**: Offline-capable ranger view
- **Voice commands**: "Show cameras near INC-2026-0042"

## Analytics & Reporting

- **Automated daily/weekly reports**: PDF/HTML via Jinja2
- **Trend detection**: Mann-Kendall on incident rates
- **Resource allocation optimizer**: Patrol scheduling via OR-Tools
- **Cost modeling**: Fuel, personnel, equipment per patrol

## Federation & Multi-Reserve

- **Cross-reserve sync**: Incident sharing via Sync API
- **Regional dashboard**: Aggregated view for state HQ
- **Data sharing agreements**: Schema + policy per partner
- **Conflict resolution**: Last-writer-wins with audit

## Federated Learning

- **Local training**: Each reserve trains on local data
- **Model aggregation**: FedAvg on central server
- **Privacy**: No raw video leaves reserve
- **Incentive**: Better model for all participants

## Compliance & Hardening

- **FIPS 140-2**: OpenSSL FIPS mode for crypto
- **STIG hardening**: CIS benchmarks for containers
- **Penetration testing**: Annual third-party
- **Data retention policy**: Configurable per entity type
- **Right to deletion**: GDPR Art. 17 for ranger PII

## Scale Targets (Post-MVP)

| Metric | Target |
|--------|--------|
| Cameras | 500+ |
| Concurrent WS | 100+ |
| Ingest FPS (cluster) | 100+ |
| Incident latency | < 500ms p99 |
| Multi-reserve | 50+ |

## Architecture Evolution

```
MVP (Modular Monolith)
    │
    ├─→ Service Extraction (if needed)
    │     ├─ Ingest Service (Kafka + Flink)
    │     ├─ Vision Service (GPU workers, Ray)
    │     ├─ Analytics Service (ClickHouse)
    │     └─ Notification Service (Redis + Push)
    │
    └─→ Edge Fleet Management
          ├─ Balena / K3s on Jetson
          ├─ OTA model updates
          └─ Health telemetry
```

## Not Planned

- Blockchain / DLT for evidence
- Crypto tokens for ranger incentives
- Autonomous drone interception
- LLM-based report generation (hallucination risk)
- Facial recognition (explicitly excluded)
- Predictive policing / pre-crime