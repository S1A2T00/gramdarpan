# GramDarpan MongoDB Database Design

This design supports the current image-analysis pipeline and the larger smart rural governance use case.

## Core Collections

### villages

Stores one record per village or gram panchayat monitoring unit.

Fields:
- `name`, `code`, `state`, `district`, `gramPanchayat`
- `population`, `households`
- `centroid` as GeoJSON Point
- `boundary` as GeoJSON Polygon/MultiPolygon

Indexes:
- Unique `code`
- `state + district + gramPanchayat + name`
- `2dsphere` on `centroid` and `boundary`

### users

Stores admins, district officers, panchayat officers, field workers, and citizens.

Fields:
- `name`, `phone`, `email`, `passwordHash`
- `role`
- `village`
- `department`
- `isActive`

Indexes:
- Unique sparse `phone`
- Unique sparse `email`
- `role`
- `village`

### imageryscenes

Stores satellite/drone scenes used as inputs for NDVI, NDWI, and change detection.

Fields:
- `village`
- `label`
- `source`
- `capturedAt`
- `season`
- `cloudCoverPercent`
- `spatialResolutionMeters`
- `bounds`
- `bands.rgb`, `bands.nir`, `bands.red`, `bands.green`, `bands.blue`, `bands.swir`

Indexes:
- `village + capturedAt`
- Unique `village + label`
- `2dsphere` on `bounds`

### analysisruns

Stores output from the Python pipeline. This keeps report data queryable and also stores the raw report for traceability.

Fields:
- `village`
- `baselineScene`, `comparisonScene`
- `status`
- `vegetation.time1`, `vegetation.time2`
- `water.time1`, `water.time2`
- `changeDetection.vegetationLossPercent`
- `changeDetection.waterLossPercent`
- `changeDetection.changeMap`
- `changeDetection.alerts`
- `rawReport`

Indexes:
- `village + createdAt`
- `status`
- Alert severity inside `changeDetection.alerts`

### alerts

Stores actionable governance alerts created from analysis output, complaints, or manual officer review.

Fields:
- `village`
- `analysisRun`
- `asset`
- `assignedTo`
- `type`
- `severity`
- `status`
- `title`
- `message`
- `zoneId`
- `location`
- `evidence`
- `recommendations`
- `resolutionNote`

Indexes:
- `village + status + severity + createdAt`
- `type`
- `assignedTo`
- `2dsphere` on `location`

### governanceassets

Stores mapped physical and natural assets in the digital twin.

Examples:
- Pond
- Canal
- Well
- Road
- School
- Anganwadi
- Health center
- Farmland
- Forest
- Building

Fields:
- `village`
- `name`
- `type`
- `status`
- `point`
- `boundary`
- `areaSqMeters`
- `photos`
- `source`
- `lastVerifiedAt`

Indexes:
- `village + type + status`
- `2dsphere` on `point` and `boundary`

### schemes

Tracks government schemes, progress, spending, assets, and beneficiaries.

Fields:
- `village`
- `name`
- `department`
- `category`
- `financialYear`
- `budgetAllocated`
- `budgetSpent`
- `progressPercent`
- `status`
- `beneficiaries`
- `linkedAssets`

Indexes:
- `village + financialYear + category`
- `department`
- `status`

### complaints

Stores citizen reports and officer follow-up.

Fields:
- `village`
- `citizen`
- `assignedTo`
- `category`
- `title`
- `description`
- `status`
- `priority`
- `location`
- `attachments`
- `linkedAlert`
- `resolutionNote`

Indexes:
- `village + status + priority + createdAt`
- `category`
- `assignedTo`
- `2dsphere` on `location`

## Relationships

- A `Village` has many `Users`, `ImageryScenes`, `AnalysisRuns`, `GovernanceAssets`, `Alerts`, `Schemes`, and `Complaints`.
- An `AnalysisRun` compares two `ImageryScenes`.
- An `AnalysisRun` can create many `Alerts`.
- An `Alert` can be assigned to a `User`.
- An `Alert` can point to a `GovernanceAsset`.
- A `Complaint` can become or link to an `Alert`.
- A `Scheme` can link to multiple `GovernanceAssets`.

## Suggested API Endpoints

Villages:
- `POST /api/villages`
- `GET /api/villages`
- `GET /api/villages/:id`

Imagery:
- `POST /api/imagery-scenes`
- `GET /api/imagery-scenes?village=<id>`

Analysis:
- `POST /api/analysis-runs`
- `GET /api/analysis-runs?village=<id>`
- `GET /api/analysis-runs/:id`

Alerts:
- `GET /api/alerts?village=<id>&status=open`
- `PATCH /api/alerts/:id/assign`
- `PATCH /api/alerts/:id/resolve`

Assets:
- `POST /api/assets`
- `GET /api/assets?village=<id>&type=pond`
- `PATCH /api/assets/:id`

Schemes:
- `POST /api/schemes`
- `GET /api/schemes?village=<id>&financialYear=2026-27`
- `PATCH /api/schemes/:id/progress`

Complaints:
- `POST /api/complaints`
- `GET /api/complaints?village=<id>&status=submitted`
- `PATCH /api/complaints/:id/status`

## Importing Current Python Report

The current Python report at `output/analysis_report.json` maps directly into `analysisruns`.

Use:

```http
POST /api/analysis-runs
Content-Type: application/json

{
  "village": "<mongo-village-id>",
  "baselineScene": "<optional-scene-id>",
  "comparisonScene": "<optional-scene-id>",
  "report": {
    "vegetation_analysis": {},
    "water_analysis": {},
    "change_detection": {}
  }
}
```

The endpoint stores queryable NDVI/NDWI metrics, zone-level vegetation metrics, change map links, raw report JSON, and actionable alert records.

## Backend Folder

```text
backend/
  src/
    config/db.js
    models/
    routes/
    server.js
```
