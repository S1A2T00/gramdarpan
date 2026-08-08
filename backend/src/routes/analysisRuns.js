import express from "express";
import { AnalysisRun } from "../models/AnalysisRun.js";
import { Alert } from "../models/Alert.js";

export const analysisRunsRouter = express.Router();

function fileFromPath(path) {
  return path ? { url: path } : undefined;
}

function mapVegetationSnapshot(snapshot) {
  if (!snapshot) return undefined;

  return {
    label: snapshot.label,
    meanNdvi: snapshot.mean_ndvi,
    healthStatus: snapshot.health_status,
    vegetationPixelPercent: snapshot.vegetation_pixel_percent,
    heatmap: fileFromPath(snapshot.heatmap_path),
    zones: (snapshot.zones || []).map((zone) => ({
      zoneId: zone.zone_id,
      meanNdvi: zone.mean_ndvi,
      healthStatus: zone.health_status
    }))
  };
}

function mapWaterSnapshot(snapshot) {
  if (!snapshot) return undefined;

  return {
    label: snapshot.label,
    waterAreaPercent: snapshot.water_area_percent,
    status: snapshot.status,
    mask: fileFromPath(snapshot.mask_path)
  };
}

analysisRunsRouter.get("/", async (req, res, next) => {
  try {
    const filter = req.query.village ? { village: req.query.village } : {};
    const runs = await AnalysisRun.find(filter)
      .sort({ createdAt: -1 })
      .limit(Number(req.query.limit || 25))
      .populate("village", "name code district state");

    res.json({ data: runs });
  } catch (error) {
    next(error);
  }
});

analysisRunsRouter.get("/:id", async (req, res, next) => {
  try {
    const run = await AnalysisRun.findById(req.params.id)
      .populate("village", "name code district state")
      .populate("baselineScene comparisonScene");

    if (!run) {
      return res.status(404).json({ error: "Analysis run not found" });
    }

    res.json({ data: run });
  } catch (error) {
    next(error);
  }
});

analysisRunsRouter.post("/", async (req, res, next) => {
  try {
    const { village, baselineScene, comparisonScene, report } = req.body;

    if (!village || !report) {
      return res.status(400).json({ error: "village and report are required" });
    }

    const change = report.change_detection || {};
    const run = await AnalysisRun.create({
      village,
      baselineScene,
      comparisonScene,
      status: "completed",
      startedAt: new Date(),
      completedAt: new Date(),
      vegetation: {
        time1: mapVegetationSnapshot(report.vegetation_analysis?.time1),
        time2: mapVegetationSnapshot(report.vegetation_analysis?.time2)
      },
      water: {
        time1: mapWaterSnapshot(report.water_analysis?.time1),
        time2: mapWaterSnapshot(report.water_analysis?.time2)
      },
      changeDetection: {
        label: change.label,
        vegetationLossPercent: change.vegetation_loss_percent,
        waterLossPercent: change.water_loss_percent,
        changeMap: fileFromPath(change.change_map_path),
        alerts: change.alerts || []
      },
      rawReport: report
    });

    const alerts = await Alert.insertMany(
      (change.alerts || []).map((alert) => ({
        village,
        analysisRun: run._id,
        type: alert.type === "Water Body Shrinkage" ? "water_body_shrinkage" : "vegetation_decline",
        severity: alert.severity,
        title: alert.type,
        message: alert.message,
        status: "open"
      }))
    );

    res.status(201).json({ data: run, alertsCreated: alerts.length });
  } catch (error) {
    next(error);
  }
});
