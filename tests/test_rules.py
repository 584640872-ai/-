import sys
import sqlite3
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
from modules.assignment import choose_consultant
from modules.workflow import validate_transition
from modules.permissions import can_read_lead, can_reveal_contact

class RulesTest(unittest.TestCase):
    def candidate(self, id, count, weight=1, **kw):
        return dict(id=id, daily_assigned=count, weight=weight, enabled=True,
                    on_duty=True, disease_ids=[1], region_ids=[], daily_capacity=30, **kw)
    def test_weight_and_capacity(self):
        a,b=self.candidate(1,10,2),self.candidate(2,4)
        self.assertEqual(choose_consultant([a,b],1,2),2)
        b['daily_capacity']=4
        self.assertEqual(choose_consultant([a,b],1,2),1)
        a['on_duty']=False
        self.assertIsNone(choose_consultant([a,b],1,2))
    def test_matching_and_tie(self):
        a,b=self.candidate(1,0,last_assigned_at='2026-09-02'),self.candidate(2,0,last_assigned_at='2026-09-01')
        self.assertEqual(choose_consultant([a,b],1,2),2)
        b['region_ids']=[3]
        self.assertEqual(choose_consultant([a,b],1,2),1)
        self.assertIsNone(choose_consultant([a,b],9,2))
    def test_transfer_revokes(self):
        lead=dict(created_by=1,assigned_to=2,team_id=1,accepted_at='now')
        user=dict(id=2,role='consultant',team_id=1,enabled=True)
        self.assertTrue(can_reveal_contact(user,lead))
        lead['assigned_to']=3
        self.assertFalse(can_read_lead(user,lead))
        user.update(id=1,role='operator')
        self.assertTrue(can_read_lead(user,lead))
        self.assertFalse(can_reveal_contact(user,lead))
        user['enabled']=False
        self.assertFalse(can_read_lead(user,lead))
    def test_workflow(self):
        with self.assertRaises(ValueError): validate_transition('accepted','won',{})
        with self.assertRaises(ValueError): validate_transition('accepted','followup_required',{'reason':'未通过'})
        validate_transition('accepted','followup_required',{'reason':'未通过','next_followup_at':'tomorrow'})
        with self.assertRaises(ValueError): validate_transition('arrived','won',{'project':'demo','deal_at':'now','amount_cents':-1})
    def test_schema(self):
        db=sqlite3.connect(':memory:')
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript((ROOT/'db/migrations/001_initial.sql').read_text())
        db.execute("INSERT INTO audit_logs(action,request_id) VALUES ('test','r1')")
        with self.assertRaises(sqlite3.IntegrityError): db.execute('DELETE FROM audit_logs')
        with self.assertRaises(sqlite3.IntegrityError): db.execute("INSERT INTO users(team_id,login,display_name,password_hash,role) VALUES (99,'demo','demo','hash','operator')")
        db.close()
if __name__=='__main__': unittest.main()
