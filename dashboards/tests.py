from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dashboards.models import QuestionBank, QuestionChoice, QuestionCategory, Role, Permission, RolePermission, UserRole

User = get_user_model()

class QuestionBankTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password123',
            role='TEACHER'
        )
        self.client.login(username='teacher', password='password123')
        
        # Setup Permissions
        create_perm = Permission.objects.create(
            code='create_question',
            name='Create Question',
            description='Create questions',
            category='question_bank'
        )
        edit_perm = Permission.objects.create(
            code='edit_question',
            name='Edit Question',
            description='Edit questions',
            category='question_bank'
        )
        
        # Setup Role
        role = Role.objects.create(
            name='Teacher',
            role_type='teacher'
        )
        RolePermission.objects.create(role=role, permission=create_perm)
        RolePermission.objects.create(role=role, permission=edit_perm)
        
        # Assign Role to User
        UserRole.objects.create(user=self.user, role=role)
        
        # Create a category
        self.category = QuestionCategory.objects.create(
            name='Math',
            created_by=self.user
        )

    def test_create_objective_question(self):
        """Test creating an objective question with choices"""
        url = reverse('question_bank_create')
        
        data = {
            'text': 'What is 2 + 2?',
            'type': 'objective',
            'category': self.category.id,
            'difficulty': 'easy',
            'marks': 2,
            'explanation': 'Simple math',
            'correct_choice': '1',  # Index of correct choice (0-based)
            'choice_text_0': '3',
            'choice_text_1': '4',
            'choice_text_2': '5',
        }
        
        response = self.client.post(url, data)
        
        # Check redirection (success)
        self.assertEqual(response.status_code, 302)
        
        # Verify Question created
        question = QuestionBank.objects.first()
        self.assertIsNotNone(question)
        self.assertEqual(question.text, 'What is 2 + 2?')
        self.assertEqual(question.question_type, 'objective')
        self.assertEqual(question.marks, 2)
        
        # Verify Choices created
        choices = QuestionChoice.objects.filter(question=question).order_by('order')
        self.assertEqual(choices.count(), 3)
        
        # Check specific choices
        c0 = choices[0]
        self.assertEqual(c0.text, '3')
        self.assertFalse(c0.is_correct)
        
        c1 = choices[1]
        self.assertEqual(c1.text, '4')
        self.assertTrue(c1.is_correct)  # This was selected as correct
        
        c2 = choices[2]
        self.assertEqual(c2.text, '5')
        self.assertFalse(c2.is_correct)

    def test_edit_objective_question(self):
        """Test editing an objective question and updating choices"""
        # Create initial question
        question = QuestionBank.objects.create(
            text='Original Question',
            question_type='objective',
            created_by=self.user
        )
        QuestionChoice.objects.create(question=question, text='Old 1', order=0)
        QuestionChoice.objects.create(question=question, text='Old 2', order=1)
        
        url = reverse('question_bank_edit', args=[question.id])
        
        # New data
        data = {
            'text': 'Updated Question',
            'type': 'objective',
            'marks': 5,
            'correct_choice': '0',
            'choice_text_0': 'New 1',
            'choice_text_1': 'New 2',
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify updates
        question.refresh_from_db()
        self.assertEqual(question.text, 'Updated Question')
        self.assertEqual(question.marks, 5)
        
        # Verify choices replaced
        choices = question.choices.all().order_by('order')
        self.assertEqual(choices.count(), 2)
        self.assertEqual(choices[0].text, 'New 1')
        self.assertTrue(choices[0].is_correct)
        self.assertEqual(choices[1].text, 'New 2')
        self.assertFalse(choices[1].is_correct)
