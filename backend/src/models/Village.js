import mongoose from "mongoose";
import { pointSchema, polygonSchema } from "./common.js";

const villageSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, index: true },
    code: { type: String, required: true, trim: true, uppercase: true, unique: true },
    district: { type: String, required: true, trim: true, index: true },
    state: { type: String, required: true, trim: true, index: true },
    gramPanchayat: { type: String, trim: true, index: true },
    population: Number,
    households: Number,
    centroid: pointSchema,
    boundary: polygonSchema,
    baselineYear: Number,
    metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
  },
  { timestamps: true }
);

villageSchema.index({ centroid: "2dsphere" });
villageSchema.index({ boundary: "2dsphere" });
villageSchema.index({ state: 1, district: 1, gramPanchayat: 1, name: 1 });

export const Village = mongoose.model("Village", villageSchema);
