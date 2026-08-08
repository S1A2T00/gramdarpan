import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import helmet from "helmet";
import { connectDb } from "./config/db.js";
import { analysisRunsRouter } from "./routes/analysisRuns.js";
import { villagesRouter } from "./routes/villages.js";

dotenv.config();

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json({ limit: "10mb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "gramdarpan-backend" });
});

app.use("/api/villages", villagesRouter);
app.use("/api/analysis-runs", analysisRunsRouter);

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === "production" ? "Internal server error" : err.message
  });
});

const port = Number(process.env.PORT || 5000);

connectDb()
  .then(() => {
    app.listen(port, () => {
      console.log(`GramDarpan backend running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to start server", error);
    process.exit(1);
  });
