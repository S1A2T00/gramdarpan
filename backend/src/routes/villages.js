import express from "express";
import { Village } from "../models/Village.js";

export const villagesRouter = express.Router();

villagesRouter.get("/", async (req, res, next) => {
  try {
    const filter = {};
    if (req.query.state) filter.state = req.query.state;
    if (req.query.district) filter.district = req.query.district;

    const villages = await Village.find(filter).sort({ state: 1, district: 1, name: 1 });
    res.json({ data: villages });
  } catch (error) {
    next(error);
  }
});

villagesRouter.post("/", async (req, res, next) => {
  try {
    const village = await Village.create(req.body);
    res.status(201).json({ data: village });
  } catch (error) {
    next(error);
  }
});
