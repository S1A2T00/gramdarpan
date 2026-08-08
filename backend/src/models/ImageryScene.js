import mongoose from "mongoose";
import { fileAssetSchema, polygonSchema } from "./common.js";

const imagerySceneSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    label: { type: String, required: true, trim: true },
    source: {
      type: String,
      enum: ["sentinel_2", "landsat", "drone", "bhuvan", "manual_upload", "sample"],
      default: "manual_upload",
      index: true
    },
    capturedAt: { type: Date, required: true, index: true },
    season: {
      type: String,
      enum: ["kharif", "rabi", "zaid", "monsoon", "summer", "winter", "unknown"],
      default: "unknown"
    },
    cloudCoverPercent: { type: Number, min: 0, max: 100 },
    spatialResolutionMeters: Number,
    bounds: polygonSchema,
    bands: {
      rgb: fileAssetSchema,
      nir: fileAssetSchema,
      red: fileAssetSchema,
      green: fileAssetSchema,
      blue: fileAssetSchema,
      swir: fileAssetSchema
    },
    metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
  },
  { timestamps: true }
);

imagerySceneSchema.index({ bounds: "2dsphere" });
imagerySceneSchema.index({ village: 1, capturedAt: -1 });
imagerySceneSchema.index({ village: 1, label: 1 }, { unique: true });

export const ImageryScene = mongoose.model("ImageryScene", imagerySceneSchema);
