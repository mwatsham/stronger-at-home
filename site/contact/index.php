<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contact | Stronger at Home Physiotherapy</title>
  <meta name="description" content="Contact Stronger at Home Physiotherapy to request an appointment or ask about a home visit.">
  <link rel="canonical" href="https://www.stronger-at-home.co.uk/contact/">
  <link rel="stylesheet" href="/assets/css/brand-tokens.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  <script src="/assets/js/site.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header">
    <a href="/" aria-label="Stronger at Home Physiotherapy, home">
      <img src="/assets/images/stronger-at-home-logo.png" alt="Stronger at Home Physiotherapy by Melanie Watsham" width="512" height="160">
    </a>
    <button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-navigation">Menu</button>
    <nav id="primary-navigation" aria-label="Primary">
      <a href="/">Home</a><a href="/about/">About Melanie</a>
      <a href="/how-i-can-help/">How I can help</a>
      <a href="/appointments-and-fees/">Appointments &amp; fees</a>
      <a href="/contact/">Contact</a>
      <a class="button" href="/contact/#appointment-request">Request an appointment</a>
    </nav>
  </header>
  <main id="main-content" class="contact-page">
    <section class="page-intro contact-intro" aria-labelledby="contact-heading">
      <p class="eyebrow">Appointments and enquiries</p>
      <h1 id="contact-heading">Contact Stronger at Home Physiotherapy</h1>
      <p class="lead">You can request an appointment by email, phone or this website enquiry form.</p>
      <div class="contact-methods" aria-label="Contact Melanie">
        <a class="contact-method" href="tel:+447843497871"><span>Call Melanie</span>+447843497871</a>
        <a class="contact-method" href="mailto:melanie@stronger-at-home.co.uk"><span>Email Melanie</span>melanie@stronger-at-home.co.uk</a>
      </div>
    </section>

    <section class="contact-form-section" aria-labelledby="appointment-request-heading">
      <div class="section-heading narrow-heading">
        <p class="eyebrow">Website enquiry</p>
        <h2 id="appointment-request-heading">Request an appointment</h2>
      </div>
      <form id="appointment-request" class="appointment-form" method="post" action="/api/enquiry.php" novalidate>
        <p>Use this form to request an appointment. Melanie will contact you directly to confirm availability.</p>
        <p class="notice">Please do not include detailed or urgent medical information.</p>
        <div class="form-status" data-form-status role="status" aria-live="polite" tabindex="-1"></div>

        <div class="form-field">
          <label for="name">Name <span aria-hidden="true">(required)</span></label>
          <input id="name" name="name" autocomplete="name" required maxlength="100">
        </div>
        <div class="form-field">
          <label for="email">Email address</label>
          <input id="email" name="email" type="email" autocomplete="email" maxlength="254" aria-describedby="contact-method-hint">
        </div>
        <div class="form-field">
          <label for="phone">Phone number</label>
          <input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="30" aria-describedby="contact-method-hint">
        </div>
        <p class="field-hint" id="contact-method-hint">Please provide an email address or phone number, and select the way you would prefer Melanie to contact you.</p>
        <div class="form-field">
          <label for="preferred-contact">Preferred contact method <span aria-hidden="true">(required)</span></label>
          <select id="preferred-contact" name="preferred_contact" required>
            <option value="email">Email</option>
            <option value="phone">Phone</option>
          </select>
        </div>
        <div class="form-field">
          <label for="postcode">Postcode <span aria-hidden="true">(required)</span></label>
          <input id="postcode" name="postcode" autocomplete="postal-code" required maxlength="10">
        </div>
        <div class="form-field">
          <label for="message">Short enquiry <span aria-hidden="true">(required)</span></label>
          <textarea id="message" name="message" required minlength="10" maxlength="1000" aria-describedby="message-hint"></textarea>
          <p class="field-hint" id="message-hint">Please keep this to a short, non-urgent appointment enquiry.</p>
        </div>
        <div class="form-field form-field-checkbox">
          <label><input name="privacy_acknowledged" type="checkbox" value="1" required> I have read the <a href="/privacy/">privacy notice</a>. <span aria-hidden="true">(required)</span></label>
        </div>
        <div class="honeypot" aria-hidden="true">
          <label for="website">Leave this field blank</label>
          <input id="website" name="website" tabindex="-1" autocomplete="off">
        </div>
        <input name="csrf_token" type="hidden" value="<?= htmlspecialchars($csrfToken ?? '', ENT_QUOTES, 'UTF-8') ?>">
        <button type="submit">Send appointment request</button>
      </form>
    </section>
  </main>
  <footer>Melanie Watsham trading as Stronger at Home Physiotherapy</footer>
</body>
</html>
