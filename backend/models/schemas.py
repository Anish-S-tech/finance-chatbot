"""Pydantic models for request / response validation."""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    reply: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None


# ── Financial Tools ──────────────────────────────────────────────────────────

class CompoundInterestRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Initial amount")
    rate: float = Field(..., gt=0, description="Annual interest rate (%)")
    years: float = Field(..., gt=0, description="Number of years")
    compounds_per_year: int = Field(12, gt=0, description="Times compounded per year")


class CompoundInterestResponse(BaseModel):
    future_value: float
    total_interest: float
    principal: float
    effective_rate: float
    yearly_breakdown: List[dict]


class EMIRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount")
    rate: float = Field(..., gt=0, description="Annual interest rate (%)")
    tenure_months: int = Field(..., gt=0, description="Loan tenure in months")


class EMIResponse(BaseModel):
    emi: float
    total_payment: float
    total_interest: float
    principal: float


class SIPRequest(BaseModel):
    monthly_investment: float = Field(..., gt=0)
    rate: float = Field(..., gt=0, description="Expected annual return (%)")
    years: int = Field(..., gt=0)


class SIPResponse(BaseModel):
    future_value: float
    total_invested: float
    wealth_gained: float


class InflationRequest(BaseModel):
    amount: float = Field(..., gt=0)
    rate: float = Field(..., gt=0, description="Annual inflation rate (%)")
    years: int = Field(..., gt=0)


class InflationResponse(BaseModel):
    future_value: float
    purchasing_power: float
    loss_percentage: float
