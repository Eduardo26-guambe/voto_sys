import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import e_votos, est, p_votos, pres, s_votos, sec


class VotingFlowTests(TestCase):
    def setUp(self):
        self.voter = User.objects.create_user(
            username='voter',
            email='voter@example.com',
            password='ValidPassword123!',
        )
        self.staff = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='ValidPassword123!',
            is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='ValidPassword123!',
        )
        self.president = pres.objects.create(
            nome='Presidente',
            foto='pic/presidente.jpg',
            descricao='Descrição',
            propostas='Propostas',
        )
        self.secretary = sec.objects.create(
            nome='Secretário',
            foto='secretario.jpg',
            descricao='Descrição',
            propostas='Propostas',
        )
        self.statistician = est.objects.create(
            nome='Estatístico',
            foto='estatistico.jpg',
            descricao='Descrição',
            propostas='Propostas',
        )

    def test_ballot_requires_login_and_records_one_vote_per_office(self):
        response = self.client.get(reverse('main_render'))
        self.assertRedirects(
            response,
            f"{reverse('login_render')}?next={reverse('main_render')}",
        )

        self.client.force_login(self.voter)
        ballot = {
            'pr': self.president.pk,
            'sc': self.secretary.pk,
            'es': self.statistician.pk,
        }
        response = self.client.post(reverse('submeter_voto'), ballot)
        self.assertRedirects(response, reverse('main_render'))
        self.assertEqual(p_votos.objects.count(), 1)
        self.assertEqual(s_votos.objects.count(), 1)
        self.assertEqual(e_votos.objects.count(), 1)
        self.client.post(reverse('submeter_voto'), ballot)
        self.assertEqual(p_votos.objects.count(), 1)
        self.assertEqual(s_votos.objects.count(), 1)
        self.assertEqual(e_votos.objects.count(), 1)

    def test_voter_can_log_in_with_email(self):
        response = self.client.post(
            reverse('logar'),
            {'email': self.voter.email, 'senha': 'ValidPassword123!'},
        )
        self.assertRedirects(response, reverse('main_render'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.voter.pk)

    def test_existing_public_pages_render(self):
        for page in ('login_render', 'reg_render', 'admin_render', 'password_reset'):
            with self.subTest(page=page):
                self.assertEqual(self.client.get(reverse(page)).status_code, 200)

        self.client.force_login(self.voter)
        response = self.client.get(reverse('main_render'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertContains(response, 'Presidente')
        self.assertContains(response, 'src="/static/pic/presidente.jpg"')

    def test_registration_and_superuser_login(self):
        response = self.client.post(
            reverse('reg_render'),
            {
                'nome': 'new-voter',
                'email': 'new-voter@example.com',
                'senha': 'Purple-Bicycle-9!Spiral',
            },
        )
        self.assertRedirects(response, reverse('login_render'))
        self.assertTrue(User.objects.filter(email='new-voter@example.com').exists())

        response = self.client.post(
            reverse('admin_render'),
            {'user': self.superuser.username, 'chave': 'ValidPassword123!'},
        )
        self.assertRedirects(response, reverse('resultados'))
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            self.superuser.pk,
        )

    def test_results_require_superuser_access(self):
        response = self.client.get(reverse('resultados'))
        self.assertRedirects(
            response,
            f"{reverse('admin_render')}?next={reverse('resultados')}",
        )

        self.client.force_login(self.staff)
        response = self.client.get(reverse('resultados'))
        self.assertRedirects(
            response,
            f"{reverse('admin_render')}?next={reverse('resultados')}",
        )

        response = self.client.post(
            reverse('admin_render'),
            {'user': self.staff.username, 'chave': 'ValidPassword123!'},
        )
        self.assertContains(response, 'Credenciais administrativas inválidas.')

        self.client.force_login(self.superuser)
        p_votos.objects.create(p_id=self.president, user_id=self.voter)
        s_votos.objects.create(s_id=self.secretary, user_id=self.voter)
        e_votos.objects.create(e_id=self.statistician, user_id=self.voter)
        response = self.client.get(reverse('resultados'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertContains(response, 'Resultados da Votação')
        self.assertContains(response, 'Presidente')
        self.assertContains(response, 'Presidência')
        self.assertContains(response, '<strong>1</strong>')
        self.assertContains(response, 'href="/static/main.css"')

    def test_logout_ends_session_and_requires_post(self):
        self.client.force_login(self.voter)
        response = self.client.get(reverse('sair'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('sair'))
        self.assertRedirects(response, reverse('login_render'))
        response = self.client.get(reverse('main_render'))
        self.assertRedirects(
            response,
            f"{reverse('login_render')}?next={reverse('main_render')}",
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_page_sends_reset_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': self.voter.email},
        )
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        reset_link = re.search(
            r'/redefinir-senha/([^/\s]+)/([^/\s]+)/',
            mail.outbox[0].body,
        )
        self.assertIsNotNone(reset_link)

        confirm_url = reverse(
            'password_reset_confirm',
            kwargs={'uidb64': reset_link.group(1), 'token': reset_link.group(2)},
        )
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 302)
        confirm_form_url = response['Location']
        response = self.client.get(confirm_form_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            confirm_form_url,
            {
                'new_password1': 'AnotherValidPassword123!',
                'new_password2': 'AnotherValidPassword123!',
            },
        )
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.voter.refresh_from_db()
        self.assertTrue(self.voter.check_password('AnotherValidPassword123!'))

# Create your tests here.
