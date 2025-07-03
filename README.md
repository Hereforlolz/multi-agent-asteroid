# 🚀 Multi-Agent Asteroid Detection System

Welcome to the dev scratchpad for the first implementation.
This is NOT a public README — it’s your personal messy notes to coordinate your work + AI helpers.

## ✅ Progress Tracker
### ✅ Done
- [ ] Project repo initialized
- [ ] README scratchpad created ✅

### ⏳ In Progress
- [ ] Set up Python environment + requirements.txt
- [ ] Implement IngestAgent (reads image file from /data)
- [ ] Implement CalibrationAgent (calls astrometry.net API)
- [ ] Implement DetectionAgent (loads DeepStreaks, finds streaks)
- [ ] Implement OrbitAgent (uses Skyfield)
- [ ] Build simple orchestrator in pipeline.py

## 🐛 Bugs / Issues
- [ ] Waiting for DeepStreaks weights — may use dummy first
- [ ] Astrometry.net may fail on synthetic images

## 🚀 Ideas & Stretch Goals
- [ ] Add ExplainabilityAgent with SHAP heatmaps
- [ ] Try Discord bot alerts
- [ ] Build small Streamlit UI

## 📝 Experiments
- [ ] Try calibration with astropy.wcs
- [ ] Compare CPU vs GPU inference time

## 📊 Metrics
| Metric                  | Target |
|--------------------------|--------|
| Detection confidence     | >90%   |
| Pipeline latency         | <30s   |

## ⚙️ Repo Structure
multi-agent-asteroid/
├─ pipeline.py
├─ agents/
├─ utils/
├─ data/
├─ results/
├─ tests/
├─ requirements.txt
└─ README.md

# 🌌 Let's do this.
