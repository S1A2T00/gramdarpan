import mongoose from "mongoose";

export const pointSchema = new mongoose.Schema(
  {
    type: {
      type: String,
      enum: ["Point"],
      required: true,
      default: "Point"
    },
    coordinates: {
      type: [Number],
      required: true,
      validate: {
        validator: (value) => value.length === 2,
        message: "Point coordinates must be [longitude, latitude]"
      }
    }
  },
  { _id: false }
);

export const polygonSchema = new mongoose.Schema(
  {
    type: {
      type: String,
      enum: ["Polygon", "MultiPolygon"],
      required: true
    },
    coordinates: {
      type: [],
      required: true
    }
  },
  { _id: false }
);

export const fileAssetSchema = new mongoose.Schema(
  {
    url: { type: String, required: true },
    storageKey: String,
    mimeType: String,
    sizeBytes: Number,
    checksum: String
  },
  { _id: false }
);
