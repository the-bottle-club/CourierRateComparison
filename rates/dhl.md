# DHL eCommerce UK — Rates & Surcharges

**Status:** Indicative rates received — for The Bottle Club.
**Service:** Next Day (standard) with optional timed add-ons.
**Max parcel weight:** 30kg standard. Heavy weight surcharges apply 30–36kg+.

---

## Zone Structure

| Zone | Coverage |
|------|----------|
| Zone A | England & Wales (standard) |
| Zone B | Central Scotland |
| Zone C | Highlands & Islands, Northern Ireland |
| Zone D | Isle of Man, Guernsey, Jersey |

---

## Standard Rates (Zone A / B — England, Wales, Central Scotland)

| HTML Weight Band | 1st Parcel |
|-----------------|------------|------------------------------------------------|
| 0–2kg | £4.65 |
| 2–3kg | £4.65 |
| 3–15kg | £4.65 |
| 15–20kg | £4.65 |
| 20–30kg | £4.65 |

Flat rate regardless of weight band (up to 30kg).

---

## Extended Region Rates

| Region | Postcodes | 1st Parcel | 2nd+ Parcels | Notes |
|--------|-----------|------------|--------------|-------|
| Highlands & Islands / Northern Ireland | Zone C | £12.00 | Up to 30kg per parcel |
| Isle of Man / Channel Islands | Zone D | £15.00 | Up to 30kg per parcel |
| Isle of Wight & Scilly | PO30–41, TR21–25 | £4.60 + £5.99 surcharge = £10.59 | — | Zone A base + surcharge |

---

## Timed Service Add-ons (added on top of base rate per shipment)

| Service | Add-on |
|---------|--------|
| Next Working Day by Noon | +£2.50 |
| Next Working Day by 10:30am | +£6.89 |
| Next Working Day by 9:00am | +£9.54 |
| Saturday delivery (standard) | +£7.42 |
| Saturday by 10:30am | +£12.19 |
| Saturday by 9:00am | +£15.90 |

---

## Surcharges

**Live surcharge reference page (check before finalising any cost model):**
- Fuel surcharge: https://www.dhl.com/pl-en/ecommerce/business-customers/customer-services/fuel-surcharge.html

The figures below were taken from the DHL indicative rates document (March 2026). Verify against the live page above before use as these change regularly.

### Per Shipment (fixed)

| Surcharge | Amount | Notes |
|-----------|--------|-------|
| Congestion | £0.75 per shipment (as quoted Mar 2026) | Applied to all shipments. Verify current rate with DHL account manager. |
| Fuel & Road | **15.25%** of base rate (April 2026, up to 31.5kg) | Indexed monthly to Polish diesel (Orlen S.A.). Changes on the 1st of each month. Check https://www.dhl.com/pl-en/ecommerce/business-customers/customer-services/fuel-surcharge.html — note this is the Polish index page; confirm with DHL account manager for UK-specific rate. |
| Isle of Wight / Scilly Isles | +£5.99 per shipment | PO30–PO41, TR21–TR25 |
| Return to Sender | £4.50 per shipment | |

### Parcel-Specific (conditional)

| Surcharge | Amount | Trigger |
|-----------|--------|---------|
| Oversized / Out of gauge | £15.00 per item | Parcels exceeding max dimensions |
| Heavy weight 30.01–32kg | +£10.00 per item | |
| Heavy weight 32.01–34kg | +£15.00 per item | |
| Heavy weight 34.01–36kg | +£30.00 per item | |
| Heavy weight 36kg+ | +£40.00 per item | |
| Long length 120–139.99cm | +£6.00 | |
| Long length 140–159.99cm | +£7.50 | |
| Long length 160cm–340cm+ | +£9.00 to +£76.00 | Graduated scale |

---

## Surcharge-Inclusive Rates (for toggle)

Applying fuel 24.5% (April 2026, up to 31.5kg) + congestion £0.75 (from Mar 2026 indicative rates).
Note: courier-data.js shows 0–2kg base as £4.80 (not £4.90 as shown in the Standard Rates table above — minor discrepancy in source documents; £4.80 used in toggle calc for 0–2kg).

| HTML Weight Band | Base (1st parcel) | + Fuel 24.5% | + Congestion £0.75 | Total |
|-----------------|-------------------|--------------|--------------------|-------|
| 0–2kg | £4.80 | £1.18 | £0.75 | **£6.73** |
| 2–3kg | £4.90 | £1.20 | £0.75 | **£6.85** |
| 3–15kg | £4.90 | £1.20 | £0.75 | **£6.85** |
| 15–20kg | £4.90 | £1.20 | £0.75 | **£6.85** |
| 20–30kg | £4.90 | £1.20 | £0.75 | **£6.85** |

Note: Fuel surcharge changes monthly — check https://www.dhl.com/pl-en/ecommerce/business-customers/customer-services/fuel-surcharge.html (Polish index) and confirm with DHL account manager for UK rate. Update SURCHARGE_DATA in the HTML when the rate changes.
Last calculated: April 2026 (fuel at 24.5%).
