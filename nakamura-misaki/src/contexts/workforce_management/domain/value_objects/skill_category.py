"""Skill category value object for workforce management"""

from enum import Enum


class SkillCategory(str, Enum):
    """Business skill categories"""

    CUSTOMER_SUPPORT = "顧客対応"
    LOGISTICS = "物流"
    APPRAISAL = "査定・修理"
    SALES = "販売"
    MANAGEMENT = "管理"
    STORE_OPERATION = "店舗"
