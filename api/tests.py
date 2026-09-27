from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Company, KBEntry, QueryLog


class TeamBoardAPITests(APITestCase):
    def setUp(self):
        KBEntry.objects.create(question='What is select_related?', answer='It joins related rows.', category='database')

    def test_register_creates_company_and_key(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'acme', 'password': 'securepass123',
            'company_name': 'Acme Corp', 'email': 'dev@acme.test',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['api_key'])
        self.assertEqual(Company.objects.get(user__username='acme').company_name, 'Acme Corp')

    def test_query_requires_auth_and_logs_zero_results(self):
        unauthenticated = self.client.post('/api/kb/query/', {'search': 'missing'}, format='json')
        self.assertEqual(unauthenticated.status_code, 401)
        user = User.objects.create_user(username='client', password='securepass123')
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/kb/query/', {'search': 'missing'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(QueryLog.objects.count(), 1)

    def test_client_cannot_access_usage_summary(self):
        user = User.objects.create_user(username='client', password='securepass123')
        self.client.force_authenticate(user=user)
        self.assertEqual(self.client.get('/api/admin/usage-summary/').status_code, 403)

    def test_admin_can_access_usage_summary(self):
        user = User.objects.create_user(username='admin', password='securepass123')
        user.company.role = Company.Role.ADMIN
        user.company.save(update_fields=['role'])
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/admin/usage-summary/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_queries'], 0)
