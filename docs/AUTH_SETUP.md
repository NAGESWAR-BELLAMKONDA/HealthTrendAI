# Authentication and first deployment setup

## Sign-up and role assignment
- Supabase Auth email/password sign-up is implemented in the web application.
- Hosted Supabase projects have email confirmation enabled by default; verify that **Authentication → Sign In / Providers → Email → Confirm email** remains enabled.
- Every new account is assigned the least-privilege `viewer` role.
- The project has no registered users yet. After the project owner signs up and confirms their email, the owner account must be promoted to `admin` once by the project owner through the Supabase SQL editor. Do not make the first public signup an administrator automatically.
- After the initial administrator is provisioned, the User Access page can assign `viewer`, `researcher`, `data_analyst`, and `admin` roles.
- Role checks are enforced in PostgreSQL RLS. Hiding a navigation item is not the security boundary.

## Gmail delivery / SMTP
Supabase's default SMTP is for testing: it only sends to authorized team email addresses and has a very low project-wide rate limit. For verification emails to ordinary Gmail inboxes and real users, configure a custom SMTP provider.

1. Create a sender account with an SMTP provider such as Resend, Brevo, Postmark, SendGrid or AWS SES.
2. Verify the sender domain/address and configure the provider's DNS instructions (SPF/DKIM; DMARC recommended).
3. In Supabase Dashboard → Authentication → SMTP Settings, enable custom SMTP and enter the provider's host, port, username, password and sender address.
4. In Authentication → URL Configuration, add the final GitHub Pages URL to allowed redirect URLs. Keep the app's Site URL aligned with the deployed URL.
5. In Authentication → Email Templates, review the Confirm signup and Reset Password templates.
6. Test a new sign-up with a Gmail inbox, click the confirmation link, then sign in.

Never put SMTP credentials, Supabase service-role keys or personal access tokens in the frontend or repository. Store backend write credentials as GitHub Actions repository secrets only.

## Provision the first administrator
After the intended owner account has registered and verified its email, run this query in the Supabase SQL editor, replacing the email with the exact owner email:
```sql
update public.app_user_roles r
set role = 'admin'
from auth.users u
where r.user_id = u.id
  and lower(u.email) = lower('OWNER_EMAIL_HERE');
```
Then sign out and sign back in so the application reloads the role.

## GitHub Pages
Repository Settings → Pages → Build and deployment → Source → **GitHub Actions**. Save, then run the **Deploy HealthTrend AI to GitHub Pages** workflow from Actions. Add the resulting URL to Supabase Auth allowed redirect URLs.
