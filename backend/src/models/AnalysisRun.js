import mongoose from "mongoose";
import { fileAssetSchema } from "./common.js";

const zoneMetricSchema = new mongoose.Schema(
  {
    zoneId: { type: String, required: true },
    meanNdvi: Number,
    healthStatus: String,
    waterAreaPercent: Number,
    riskScore: { type: Number, min: 0, max: 100 }
  },
  { _id: false }
);

const vegetationSnapshotSchema = new mongoose.Schema(
  {
    label: String,
    meanNdvi: Number,
    healthStatus: String,
    vegetationPixelPercent: Number,
    heatmap: fileAssetSchema,
    zones: [zoneMetricSchema]
  },
  { _id: false }
);

const waterSnapshotSchema = new mongoose.Schema(
  {
    label: String,
    waterAreaPercent: Number,
    status: String,
    mask: fileAssetSchema
  },
  { _id: false }
);

const alertSnapshotSchema = new mongoose.Schema(
  {
    type: { type: String, required: true },
    severity: { type: String, enum: ["Low", "Medium", "High", "Critical"], required: true },
    message: { type: String, required: true },
    zoneId: String
  },
  { _id: false }
);

const analysisRunSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    baselineScene: { type: mongoose.Schema.Types.ObjectId, ref: "ImageryScene" },
    comparisonScene: { type: mongoose.Schema.Types.ObjectId, ref: "ImageryScene" },
    status: {
      type: String,
      enum: ["queued", "running", "completed", "failed"],
      default: "queued",
      index: true
    },
    pipelineVersion: { type: String, default: "python-local-v1" },
    startedAt: Date,
    completedAt: Date,
    vegetation: {
      time1: vegetationSnapshotSchema,
      time2: vegetationSnapshotSchema
    },
    water: {
      time1: waterSnapshotSchema,
      time2: waterSnapshotSchema
    },
    changeDetection: {
      label: String,
      vegetationLossPercent: Number,
      waterLossPercent: Number,
      changeMap: fileAssetSchema,
      alerts: [alertSnapshotSchema]
    },
    rawReport: mongoose.Schema.Types.Mixed,
    errorMessage: String
  },
  { timestamps: true }
);

analysisRunSchema.index({ village: 1, createdAt: -1 });
analysisRunSchema.index({ "changeDetection.alerts.severity": 1 });

export const AnalysisRun = mongoose.model("AnalysisRun", analysisRunSchema);
