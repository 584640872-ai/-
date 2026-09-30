"""后端权限规则骨架；不向运营返回咨询备注或单条成交金额。"""
def can_read_lead(user, lead):
    if not user["enabled"]:
        return False
    return (user["role"] == "admin" or
            user["role"] == "supervisor" and user["team_id"] == lead["team_id"] or
            user["role"] == "operator" and user["id"] == lead["created_by"] or
            user["role"] == "consultant" and user["id"] == lead["assigned_to"])

def can_reveal_contact(user, lead):
    return (can_read_lead(user, lead) and user["role"] == "consultant"
            and user["id"] == lead["assigned_to"] and lead.get("accepted_at") is not None)
