import mongoose from "mongoose";
import { fileAssetSchema, pointSchema, polygonSchema } from "./common.js";

const governanceAssetSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    name: { type: String, required: true, trim: true },
    type: {
      type: String,
      enum: ["pond", "canal", "well", "road", "school", "anganwadi", "health_center", "farmland", "forest", "building", "other"],
      required: true,
      index: true
    },
    status: {
      type: String,
      enum: ["good", "needs_attention", "damaged", "encroached", "inactive", "unknown"],
      default: "unknown",
      index: true
    },
    point: pointSchema,
    boundary: polygonSchema,
    areaSqMeters: Number,
    photos: [fileAssetSchema],
    source: { type: String, enum: ["survey", "satellite", "drone", "department_record", "citizen_report"], default: "survey" },
    lastVerifiedAt: Date,
    metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
  },
  { timestamps: true }
);

governanceAssetSchema.index({ point: "2dsphere" });
governanceAssetSchema.index({ boundary: "2dsphere" });
governanceAssetSchema.index({ village: 1, type: 1, status: 1 });

export const GovernanceAsset = mongoose.model("GovernanceAsset", governanceAssetSchema);
