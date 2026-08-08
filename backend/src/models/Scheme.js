import mongoose from "mongoose";

const beneficiarySchema = new mongoose.Schema(
  {
    name: { type: String, required: true },
    householdId: String,
    aadhaarHash: String,
    phone: String,
    status: {
      type: String,
      enum: ["eligible", "applied", "approved", "benefit_released", "rejected"],
      default: "eligible"
    },
    lastUpdatedAt: { type: Date, default: Date.now }
  },
  { _id: false }
);

const schemeSchema = new mongoose.Schema(
  {
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", required: true, index: true },
    name: { type: String, required: true, trim: true },
    department: { type: String, required: true, trim: true, index: true },
    category: {
      type: String,
      enum: ["agriculture", "water", "housing", "sanitation", "employment", "health", "education", "infrastructure", "other"],
      default: "other",
      index: true
    },
    financialYear: { type: String, required: true, index: true },
    budgetAllocated: Number,
    budgetSpent: Number,
    progressPercent: { type: Number, min: 0, max: 100, default: 0 },
    status: {
      type: String,
      enum: ["planned", "active", "delayed", "completed", "paused"],
      default: "planned",
      index: true
    },
    beneficiaries: [beneficiarySchema],
    linkedAssets: [{ type: mongoose.Schema.Types.ObjectId, ref: "GovernanceAsset" }]
  },
  { timestamps: true }
);

schemeSchema.index({ village: 1, financialYear: 1, category: 1 });

export const Scheme = mongoose.model("Scheme", schemeSchema);
