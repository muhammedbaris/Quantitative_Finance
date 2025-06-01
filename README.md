# 📈 Fixed Income Attribution Dashboard (Work in Progress)

**Status**: 🚧 Work in Progress  
**Last Updated**: [01.06.2025]

---

## 🧠 Overview

This project aims to develop a **Fixed Income Attribution Dashboard** that decomposes portfolio-level and bond-level returns into key risk and return factors. The tool is designed to replicate the type of analysis conducted by quantitative analysts in fixed income investment roles, particularly for portfolios with corporate bond exposure.

This project is inspired by the requirements of real-world investment quant roles, especially those focusing on **portfolio construction**, **risk attribution**, and **credit analytics**.

---

## 🎯 Project Goals

- Build a **quantitative attribution framework** for fixed income portfolios.
- Decompose returns into components such as:
  - **Carry**
  - **Roll-down**
  - **Credit spread changes**
  - **Interest rate (yield curve) shifts**
  - **Selection or residual effects**
- Deliver an **interactive dashboard** to visualize performance attribution over time and by bond, sector, or risk factor.
- Provide a **replicable, modular codebase** written in Python using best practices in data science and financial engineering.

---

## 🗂️ Planned Features

### ✔️ Attribution Engine
- Return decomposition at both **bond** and **portfolio** level.
- Support for daily, monthly, or custom-period attribution windows.
- Simulation capability if real data is unavailable.

### ✔️ Bond Analytics Toolkit
- Yield and price calculators.
- Duration and convexity metrics.
- Spread estimation (e.g., Z-spread, OAS approximation).

### ✔️ Interactive Dashboard
- Built using **Streamlit** or **Dash**.
- Visual breakdowns:
  - Attribution by bond, sector, maturity.
  - Time series of factor contributions.
  - Summary tables and risk metrics.

---

## 📁 Project Structure (Planned)

