"""业务状态规则；转派/回收属于分配事件，单独保留历史。"""
TRANSITIONS = {
    "pending_assignment": {"pending_acceptance", "invalid"},
    "pending_acceptance": {"accepted", "pending_assignment"},
    "accepted": {"wechat_added", "followup_required", "invalid"},
    "followup_required": {"wechat_added", "invalid"},
    "wechat_added": {"booked", "invalid"},
    "booked": {"arrived", "wechat_added", "invalid"},
    "arrived": {"won", "invalid"},
    "won": set(), "invalid": set(),
}
def validate_transition(before, after, payload):
    if after not in TRANSITIONS.get(before, set()):
        raise ValueError("不允许的状态变更")
    required = {"followup_required": ["reason", "next_followup_at"],
                "booked": ["hospital_id", "appointment_at"],
                "arrived": ["arrived_at"],
                "won": ["project", "amount_cents", "deal_at"],
                "invalid": ["reason"]}.get(after, [])
    if any(payload.get(k) is None or payload.get(k) == "" for k in required):
        raise ValueError("缺少状态必填结果")
    if after == "won" and (type(payload["amount_cents"]) is not int or payload["amount_cents"] < 0):
        raise ValueError("成交金额必须为非负整数分")
