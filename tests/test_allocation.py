import unittest
from backend.modules.allocation import choose

def person(id, weight=1, count=0, **changes):
    p=dict(id=id, weight=weight, assigned_today=count, enabled=True,on_duty=True,
           diseases=['demo'],regions=[],daily_capacity=20,active_capacity=50,
           active_count=0,blocked=False,last_assigned_at='')
    p.update(changes)
    return p

class AllocationTests(unittest.TestCase):
    def test_weighted_priority(self):
        self.assertEqual(choose([person('A',2,10),person('B',1,4)],'demo','gz')['id'],'B')
    def test_filters(self):
        for change in [dict(enabled=False),dict(on_duty=False),dict(diseases=[]),
                       dict(regions=['nj']),dict(assigned_today=20),dict(active_count=50),dict(blocked=True)]:
            self.assertIsNone(choose([person('A',**change)],'demo','gz'))
    def test_oldest_wins(self):
        self.assertEqual(choose([person('B',last_assigned_at='2026-09-30T02:00:00Z'),
                                person('A',last_assigned_at='2026-09-30T01:00:00Z')],'demo','gz')['id'],'A')
    def test_no_candidate(self):
        self.assertIsNone(choose([],'demo','gz'))
