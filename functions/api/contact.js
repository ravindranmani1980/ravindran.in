// Cloudflare Pages Function: POST /api/contact
// Sends the contact form as an email through SMTP (worker-mailer).
// Requires the "nodejs_compat" compatibility flag on the Pages project.
// Secrets (Pages > Settings > Variables and secrets):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS (secret), ADMIN_NOTIFICATION_EMAIL
//   FROM_EMAIL (optional; defaults to SMTP_USER)
import { WorkerMailer } from 'worker-mailer';

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

export async function onRequestPost(context) {
  const { request, env } = context;

  let data;
  const ct = request.headers.get('content-type') || '';
  try {
    if (ct.includes('application/json')) {
      data = await request.json();
    } else {
      const form = await request.formData();
      data = Object.fromEntries(form);
    }
  } catch (_) {
    return json({ ok: false, error: 'Could not read the form.' }, 400);
  }

  // Honeypot: real people leave this hidden field empty.
  if (data.company) return json({ ok: true });

  const name = (data.name || '').toString().trim().slice(0, 200);
  const email = (data.email || '').toString().trim().slice(0, 254);
  const message = (data.message || '').toString().trim().slice(0, 5000);

  if (!name || !message || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json(
      { ok: false, error: 'Please add your name, a valid email, and a message.' },
      400
    );
  }

  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ADMIN_NOTIFICATION_EMAIL } = env;
  const FROM_EMAIL = env.FROM_EMAIL || SMTP_USER;
  if (!SMTP_HOST || !SMTP_PORT || !SMTP_USER || !SMTP_PASS || !ADMIN_NOTIFICATION_EMAIL) {
    return json({ ok: false, error: 'Mail is not configured on the server.' }, 500);
  }

  const port = parseInt(SMTP_PORT, 10);
  try {
    await WorkerMailer.send(
      {
        host: SMTP_HOST,
        port,
        secure: port === 465,      // implicit TLS on 465
        startTls: port !== 465,    // STARTTLS on 587 (iCloud)
        credentials: { username: SMTP_USER, password: SMTP_PASS },
        authType: ['plain', 'login'],
      },
      {
        from: { name: 'ravindran.in contact form', email: FROM_EMAIL },
        to: ADMIN_NOTIFICATION_EMAIL,
        reply: { name, email },
        subject: 'New contact form message from ' + name,
        text: 'Name: ' + name + '\nEmail: ' + email + '\n\n' + message,
        html:
          '<p><strong>Name:</strong> ' + escapeHtml(name) +
          '<br><strong>Email:</strong> ' + escapeHtml(email) + '</p>' +
          '<p style="white-space:pre-wrap">' + escapeHtml(message) + '</p>',
      }
    );
    return json({ ok: true });
  } catch (err) {
    console.error('contact send failed:', err && err.message ? err.message : err);
    return json(
      { ok: false, error: 'Could not send right now. Please email me directly.' },
      502
    );
  }
}
