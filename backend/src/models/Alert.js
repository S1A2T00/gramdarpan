import mongoose from "mongoose";
import { fileAssetSchema, pointSchema } from "./common.js";

const alertSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    analysisRun: { type: mongoose.Schema.Types.ObjectId, ref: "AnalysisRun", index: true },
    asset: { type: mongoose.Schema.Types.ObjectId, ref: "GovernanceAsset", index: true },
    assignedTo: { type: mongoose.Schema.Types.ObjectId, ref: "User", index: true },
    type: {
      type: String,
      enum: ["vegetation_decline", "water_body_shrinkage", "encroachment", "asset_damage", "complaint", "scheme_delay", "other"],
      required: true,
      index: true
    },
    severity: {
      type: String,
      enum: ["Low", "Medium", "High", "Critical"],
      required: true,
      index: true
    },
    status: {
      type: String,
      enum: ["open", "assigned", "in_progress", "resolved", "dismissed"],
      default: "open",
      index: true
    },
    title: { type: String, required: true, trim: true },
    message: { type: String, required: true },
    zoneId: String,
    location: pointSchema,
    evidence: [fileAssetSchema],
    recommendations: [String],
    resolvedAt: Date,
    resolutionNote: String
  },
  { timestamps: true }
);

alertSchema.index({ location: "2dsphere" });
alertSchema.index({ village: 1, status: 1, severity: 1, createdAt: -1 });

export const Alert = mongoose.model("Alert", alertSchema);
