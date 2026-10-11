"""
Automated Integration and Unit Tests for SpendWise
Validates mode isolation, CRUD workflows, custom budget settings, and real-time analytics.
"""

import json
from datetime import datetime
import unittest
from app import create_app
from database import get_db_connection

class SpendWiseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_live_mode_empty_slate(self):
        """Live mode must start 100% empty with zero transactions."""
        res = self.client.get('/api/expenses?mode=live')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 0)

    def test_02_demo_mode_isolation(self):
        """Demo mode must contain isolated sample records."""
        res = self.client.get('/api/expenses?mode=demo')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 28)

    def test_03_live_kpis_when_empty(self):
        """When empty, KPIs report 0 spent, 0 count, and null highest expense."""
        res = self.client.get('/api/analytics/summary?mode=live')
        kpis = json.loads(res.data)['data']
        self.assertEqual(kpis['total_spent'], 0.0)
        self.assertEqual(kpis['total_transactions'], 0)
        self.assertIsNone(kpis['highest_expense'])

    def test_04_custom_budget_any_value(self):
        """Users can write any positive decimal amount for monthly budget."""
        custom_amount = 3250.75
        now = datetime.now()
        payload = {
            'amount': custom_amount,
            'month': now.month,
            'year': now.year,
            'is_demo': 0
        }
        res = self.client.post('/api/budget', json=payload)
        self.assertEqual(res.status_code, 200)

        # Verify retrieved in KPI summary
        res = self.client.get(f'/api/analytics/summary?mode=live&month={now.month}&year={now.year}')
        kpis = json.loads(res.data)['data']
        self.assertEqual(kpis['budget']['limit'], custom_amount)

    def test_05_create_and_recalculate_analytics(self):
        """Adding a new expense immediately updates totals, categories, trends, and budget progress."""
        today_str = datetime.now().strftime('%Y-%m-%d')
        new_expense = {
            'title': 'Test Grocery Run',
            'amount': 95.50,
            'category': 'Groceries',
            'date': today_str,
            'payment_method': 'Credit Card',
            'notes': 'Unit test transaction'
        }
        # Create
        res = self.client.post('/api/expenses', json=new_expense)
        self.assertEqual(res.status_code, 201)
        created = json.loads(res.data)['data']
        expense_id = created['id']

        try:
            # Check KPIs
            res = self.client.get('/api/analytics/summary?mode=live')
            kpis = json.loads(res.data)['data']
            self.assertEqual(kpis['total_spent'], 95.50)
            self.assertEqual(kpis['total_transactions'], 1)
            self.assertEqual(kpis['highest_expense']['title'], 'Test Grocery Run')

            # Check Categories Breakdown
            res = self.client.get('/api/analytics/categories?mode=live')
            cats = json.loads(res.data)['data']['categories']
            self.assertEqual(len(cats), 1)
            self.assertEqual(cats[0]['name'], 'Groceries')
            self.assertEqual(cats[0]['amount'], 95.50)

            # Check Trends
            res = self.client.get('/api/analytics/trends?mode=live')
            trends = json.loads(res.data)['data']
            self.assertIn('daily', trends)
            self.assertIn('monthly', trends)

        finally:
            # Clean up test transaction to keep live database pristine
            del_res = self.client.delete(f'/api/expenses/{expense_id}')
            self.assertEqual(del_res.status_code, 200)

            # Confirm clean state restored
            res = self.client.get('/api/expenses?mode=live')
            self.assertEqual(json.loads(res.data)['data']['total_count'], 0)

    def test_06_clear_and_seed_isolation(self):
        """Clearing live expenses does not delete demo data, and seeding demo does not pollute live data."""
        # Add temporary live expense
        today_str = datetime.now().strftime('%Y-%m-%d')
        res = self.client.post('/api/expenses', json={
            'title': 'Temp Item',
            'amount': 20.00,
            'category': 'Shopping',
            'date': today_str,
            'payment_method': 'Cash'
        })
        self.assertEqual(res.status_code, 201)

        # Clear all user expenses
        res = self.client.delete('/api/expenses/clear')
        self.assertEqual(res.status_code, 200)

        # Live expenses should now be 0
        res = self.client.get('/api/expenses?mode=live')
        self.assertEqual(json.loads(res.data)['data']['total_count'], 0)

        # Demo expenses should still have 28 records!
        res = self.client.get('/api/expenses?mode=demo')
        self.assertEqual(json.loads(res.data)['data']['total_count'], 28)

        # Re-seed demo sandbox
        res = self.client.post('/api/expenses/seed')
        self.assertEqual(res.status_code, 200)

        # Live expenses must REMAIN 0!
        res = self.client.get('/api/expenses?mode=live')
        self.assertEqual(json.loads(res.data)['data']['total_count'], 0)

    def test_07_export_csv(self):
        """Export CSV endpoint delivers formatted CSV with attachment headers."""
        res = self.client.get('/api/expenses/export?mode=demo')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'text/csv')
        self.assertIn(b'Grocery Mart', res.data)

if __name__ == '__main__':
    unittest.main()

