import mongoose from "mongoose";
import { fileAssetSchema, pointSchema } from "./common.js";

const complaintSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    citizen: { type: mongoose.Schema.Types.ObjectId, ref: "User", index: true },
    assignedTo: { type: mongoose.Schema.Types.ObjectId, ref: "User", index: true },
    category: {
      type: String,
      enum: ["water", "road", "electricity", "sanitation", "crop_damage", "scheme", "encroachment", "other"],
      required: true,
      index: true
    },
    title: { type: String, required: true, trim: true },
    description: { type: String, required: true },
    status: {
      type: String,
      enum: ["submitted", "acknowledged", "assigned", "in_progress", "resolved", "rejected"],
      default: "submitted",
      index: true
    },
    priority: { type: String, enum: ["Low", "Medium", "High", "Critical"], default: "Medium", index: true },
    location: pointSchema,
    attachments: [fileAssetSchema],
    linkedAlert: { type: mongoose.Schema.Types.ObjectId, ref: "Alert" },
    resolutionNote: String,
    resolvedAt: Date
  },
  { timestamps: true }
);

complaintSchema.index({ location: "2dsphere" });
complaintSchema.index({ village: 1, status: 1, priority: 1, createdAt: -1 });

export const Complaint = mongoose.model("Complaint", complaintSchema);
