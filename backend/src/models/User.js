import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    phone: { type: String, trim: true, index: true },
    email: { type: String, trim: true, lowercase: true, index: true },
    passwordHash: { type: String, required: true, select: false },
    role: {
      type: String,
      enum: ["admin", "district_officer", "panchayat_officer", "field_worker", "citizen"],
      required: true,
      index: true
    },
    village: { type: mongoose.Schema.Types.ObjectId, ref: "Village", index: true },
    department: {
      type: String,
      enum: ["agriculture", "water", "revenue", "panchayat", "health", "education", "public_works", "other"],
      default: "other"
    },
    isActive: { type: Boolean, default: true }
  },
  { timestamps: true }
);

userSchema.index({ phone: 1 }, { unique: true, sparse: true });
userSchema.index({ email: 1 }, { unique: true, sparse: true });

export const User = mongoose.model("User", userSchema);
