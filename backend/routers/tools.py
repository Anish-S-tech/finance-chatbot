"""Financial calculator tool endpoints."""

from __future__ import annotations
import math
from fastapi import APIRouter

from backend.models.schemas import (
    CompoundInterestRequest, CompoundInterestResponse,
    EMIRequest, EMIResponse,
    SIPRequest, SIPResponse,
    InflationRequest, InflationResponse,
)

router = APIRouter(prefix="/api/tools", tags=["Financial Tools"])


@router.post("/compound-interest", response_model=CompoundInterestResponse)
def compound_interest(req: CompoundInterestRequest):
    """Calculate compound interest with yearly breakdown."""
    r = req.rate / 100
    n = req.compounds_per_year
    t = req.years
    p = req.principal

    future_value = p * (1 + r / n) ** (n * t)
    total_interest = future_value - p
    effective_rate = ((1 + r / n) ** n - 1) * 100

    # Yearly breakdown
    breakdown = []
    for year in range(1, int(t) + 1):
        fv = p * (1 + r / n) ** (n * year)
        breakdown.append({
            "year": year,
            "value": round(fv, 2),
            "interest_earned": round(fv - p, 2),
        })

    return CompoundInterestResponse(
        future_value=round(future_value, 2),
        total_interest=round(total_interest, 2),
        principal=p,
        effective_rate=round(effective_rate, 2),
        yearly_breakdown=breakdown,
    )


@router.post("/emi", response_model=EMIResponse)
def calculate_emi(req: EMIRequest):
    """Calculate Equated Monthly Installment."""
    p = req.principal
    r = req.rate / 100 / 12  # monthly rate
    n = req.tenure_months

    if r == 0:
        emi = p / n
    else:
        emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)

    total_payment = emi * n
    total_interest = total_payment - p

    return EMIResponse(
        emi=round(emi, 2),
        total_payment=round(total_payment, 2),
        total_interest=round(total_interest, 2),
        principal=p,
    )


@router.post("/sip", response_model=SIPResponse)
def calculate_sip(req: SIPRequest):
    """Calculate Systematic Investment Plan returns."""
    m = req.monthly_investment
    r = req.rate / 100 / 12  # monthly rate
    n = req.years * 12  # total months

    if r == 0:
        future_value = m * n
    else:
        future_value = m * (((1 + r) ** n - 1) / r) * (1 + r)

    total_invested = m * n
    wealth_gained = future_value - total_invested

    return SIPResponse(
        future_value=round(future_value, 2),
        total_invested=round(total_invested, 2),
        wealth_gained=round(wealth_gained, 2),
    )


@router.post("/inflation", response_model=InflationResponse)
def calculate_inflation(req: InflationRequest):
    """Calculate inflation-adjusted purchasing power."""
    r = req.rate / 100
    future_nominal = req.amount * (1 + r) ** req.years
    purchasing_power = req.amount / (1 + r) ** req.years
    loss_pct = ((req.amount - purchasing_power) / req.amount) * 100

    return InflationResponse(
        future_value=round(future_nominal, 2),
        purchasing_power=round(purchasing_power, 2),
        loss_percentage=round(loss_pct, 2),
    )
