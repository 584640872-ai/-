"""Pure allocation policy; database transaction integration is a later milestone."""
from fractions import Fraction

def choose(candidates, disease, region):
    eligible = [c for c in candidates if c['enabled'] and c['on_duty']
                and disease in c['diseases'] and (not c['regions'] or region in c['regions'])
                and c['weight'] > 0 and c['assigned_today'] < c['daily_capacity']
                and c['active_count'] < c['active_capacity'] and not c['blocked']]
    return min(eligible, key=lambda c: (Fraction(c['assigned_today'], c['weight']),
                                       c['last_assigned_at'] or '', c['id']), default=None)
