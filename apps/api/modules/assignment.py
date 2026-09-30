"""纯规则候选选择；生产分配必须在数据库事务中执行。"""
from fractions import Fraction

def choose_consultant(candidates, disease_id, region_id):
    eligible = [c for c in candidates if c["enabled"] and c["on_duty"]
                and disease_id in c["disease_ids"]
                and (not c["region_ids"] or region_id in c["region_ids"])
                and c["weight"] > 0 and c["daily_assigned"] < c["daily_capacity"]
                and not c.get("blocked_by_timeout", False)]
    if not eligible:
        return None
    return min(eligible, key=lambda c: (Fraction(c["daily_assigned"], c["weight"]),
               c.get("last_assigned_at") or "", c["id"]))["id"]
