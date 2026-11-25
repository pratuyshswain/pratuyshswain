![Pratyusha Swain — an engraved relief map in ink, sage and copper](assets/relief-cover.svg)

I'm Pratyusha, a B.Tech computer science student. I build Python tools for questions like *which customers might leave?* and *how much will a shop sell next month?* I like the work between a model and the person using it: cleaning the input, testing the prediction, and giving the result a useful interface.

[Play Contour Survey](https://raw.githack.com/pratuyshswain/pratuyshswain/main/docs/index.html) · [Browse my repositories](https://github.com/pratuyshswain?tab=repositories)

## Selected work

| Project | What you can explore |
| --- | --- |
| [Sales Forecasting Dashboard](https://github.com/pratuyshswain/Sales-Forecasting-Dashboard-) | Follow sales records through a SQLite warehouse to Holt–Winters forecasts and BI exports. |
| [Customer Retention Agent](https://github.com/pratuyshswain/customer-retention-agent) | Serve churn predictions and retention workflows through a FastAPI application. |
| [Customer Churn Prediction](https://github.com/pratuyshswain/Customer-Churn-Prediction) | Inspect a random forest classifier and its model visualizations. |
| [Mini Sales Dashboard](https://github.com/pratuyshswain/Sales-Forecasting-Dashboard-mini) | Trace synthetic retail data through a compact forecasting and risk-visualization pipeline. |

## Two small games

**[Contour Survey ↗](https://raw.githack.com/pratuyshswain/pratuyshswain/main/docs/index.html)** — Rotate a 3D landscape and identify its highest marked station. Three rounds, four stations per round. [Get the standalone HTML](https://github.com/pratuyshswain/pratuyshswain/raw/refs/heads/main/docs/index.html).

**Beat the baseline** — A shop sold **80, 100, then 120 units** over three weeks. For week four, the shopkeeper predicts 120, the last observed value. Pick your forecast to reveal the actual sales and see who was closer.

<details><summary>100 units · use the three-week average</summary>

Actual sales were **135**. Your forecast missed by 35 units. The shopkeeper missed by 15 and wins this round.

</details>

<details><summary>140 units · continue the weekly trend</summary>

Actual sales were **135**. Your forecast missed by 5 units. You beat the baseline by 10 units. The next test would be to repeat this comparison over several held-out weeks.

</details>

## Open source

In [cv-benchkit PR #89](https://github.com/udayraj1238/cv-benchkit/pull/89), I added input-path validation for COCO, YOLO and VOC conversions and six regression tests. The maintainers merged the change. I used AI assistance for implementation and testing.

I work primarily with Python, SQL, pandas, scikit-learn and FastAPI. Across my featured repositories, I use pytest, Docker and GitHub Actions to check that the code runs beyond my own machine.
