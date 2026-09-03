<?php
declare(strict_types=1);

ini_set('session.use_strict_mode', '1');
ini_set('session.use_only_cookies', '1');
session_set_cookie_params([
    'secure' => true,
    'httponly' => true,
    'samesite' => 'Lax',
]);
if (!session_start()) {
    http_response_code(500);
    exit;
}

$existingToken = $_SESSION['csrf_token'] ?? null;
if (!is_string($existingToken) || preg_match('/\A[a-f0-9]{64}\z/D', $existingToken) !== 1) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
$csrfToken = $_SESSION['csrf_token'];

$flash = $_SESSION['form_flash'] ?? [];
unset($_SESSION['form_flash']);
if (!is_array($flash)) {
    $flash = [];
}

$kind = isset($flash['kind']) && is_string($flash['kind']) ? $flash['kind'] : '';
$statusMessages = [
    'success' => 'Thank you. Your appointment request has been received. Melanie will contact you to discuss availability.',
    'validation' => 'Please check the highlighted fields and try again.',
    'rate' => 'Please wait before trying again. You can also call Melanie on +447843497871 or email melanie@stronger-at-home.co.uk.',
    'delivery' => 'Your request could not be sent. Please call Melanie on +447843497871 or email melanie@stronger-at-home.co.uk.',
];
$statusMessage = $statusMessages[$kind] ?? '';

$allowedValueKeys = ['name', 'email', 'phone', 'preferred_contact', 'postcode'];
$values = [];
$flashValues = isset($flash['values']) && is_array($flash['values']) ? $flash['values'] : [];
foreach ($allowedValueKeys as $key) {
    $values[$key] = isset($flashValues[$key]) && is_string($flashValues[$key]) ? $flashValues[$key] : '';
}

$allowedErrorKeys = ['name', 'email', 'phone', 'preferred_contact', 'postcode', 'message', 'privacy_acknowledged'];
$errors = [];
$flashErrors = isset($flash['errors']) && is_array($flash['errors']) ? $flash['errors'] : [];
foreach ($allowedErrorKeys as $key) {
    if (isset($flashErrors[$key]) && is_string($flashErrors[$key])) {
        $errors[$key] = $flashErrors[$key];
    }
}

$escape = static fn(string $value): string => htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
?>
<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contact | Stronger at Home Physiotherapy</title>
  <meta name="description" content="Contact Stronger at Home Physiotherapy to request an appointment or ask about a home visit.">
  <link rel="canonical" href="https://stronger-at-home.co.uk/contact/">
  <meta property="og:title" content="Contact | Stronger at Home Physiotherapy">
  <meta property="og:description" content="Contact Stronger at Home Physiotherapy to request an appointment or ask about a home visit.">
  <meta property="og:url" content="https://stronger-at-home.co.uk/contact/">
  <meta property="og:type" content="website">
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
        <div id="form-feedback" class="form-status" data-form-status data-flash-kind="<?= $escape($kind) ?>" role="status" aria-live="polite" tabindex="-1"><?= $escape($statusMessage) ?></div>

        <div class="form-field">
          <label for="name">Name <span aria-hidden="true">(required)</span></label>
          <input id="name" name="name" autocomplete="name" required maxlength="100" value="<?= $escape($values['name']) ?>"<?= isset($errors['name']) ? ' aria-invalid="true" aria-describedby="name-error"' : '' ?>>
          <?php if (isset($errors['name'])): ?><p class="field-error" id="name-error"><?= $escape($errors['name']) ?></p><?php endif; ?>
        </div>
        <div class="form-field">
          <label for="email">Email address</label>
          <input id="email" name="email" type="email" autocomplete="email" maxlength="254" aria-describedby="contact-method-hint<?= isset($errors['email']) ? ' email-error' : '' ?>" value="<?= $escape($values['email']) ?>"<?= isset($errors['email']) ? ' aria-invalid="true"' : '' ?>>
          <?php if (isset($errors['email'])): ?><p class="field-error" id="email-error"><?= $escape($errors['email']) ?></p><?php endif; ?>
        </div>
        <div class="form-field">
          <label for="phone">Phone number</label>
          <input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="30" aria-describedby="contact-method-hint<?= isset($errors['phone']) ? ' phone-error' : '' ?>" value="<?= $escape($values['phone']) ?>"<?= isset($errors['phone']) ? ' aria-invalid="true"' : '' ?>>
          <?php if (isset($errors['phone'])): ?><p class="field-error" id="phone-error"><?= $escape($errors['phone']) ?></p><?php endif; ?>
        </div>
        <p class="field-hint" id="contact-method-hint">Please provide an email address or phone number, and select the way you would prefer Melanie to contact you.</p>
        <div class="form-field">
          <label for="preferred-contact">Preferred contact method <span aria-hidden="true">(required)</span></label>
          <select id="preferred-contact" name="preferred_contact" required <?= isset($errors['preferred_contact']) ? 'aria-invalid="true" aria-describedby="preferred-contact-error"' : '' ?>>
            <option value="email"<?= $values['preferred_contact'] !== 'phone' ? ' selected' : '' ?>>Email</option>
            <option value="phone"<?= $values['preferred_contact'] === 'phone' ? ' selected' : '' ?>>Phone</option>
          </select>
          <?php if (isset($errors['preferred_contact'])): ?><p class="field-error" id="preferred-contact-error"><?= $escape($errors['preferred_contact']) ?></p><?php endif; ?>
        </div>
        <div class="form-field">
          <label for="postcode">Postcode <span aria-hidden="true">(required)</span></label>
          <input id="postcode" name="postcode" autocomplete="postal-code" required maxlength="10" value="<?= $escape($values['postcode']) ?>"<?= isset($errors['postcode']) ? ' aria-invalid="true" aria-describedby="postcode-error"' : '' ?>>
          <?php if (isset($errors['postcode'])): ?><p class="field-error" id="postcode-error"><?= $escape($errors['postcode']) ?></p><?php endif; ?>
        </div>
        <div class="form-field">
          <label for="message">Short enquiry <span aria-hidden="true">(required)</span></label>
          <?php if (isset($errors['message'])): ?>
          <textarea id="message" name="message" required minlength="10" maxlength="1000" aria-describedby="message-hint message-error" aria-invalid="true"></textarea>
          <?php else: ?>
          <textarea id="message" name="message" required minlength="10" maxlength="1000" aria-describedby="message-hint"></textarea>
          <?php endif; ?>
          <p class="field-hint" id="message-hint">Please keep this to a short, non-urgent appointment enquiry.</p>
          <?php if (isset($errors['message'])): ?><p class="field-error" id="message-error"><?= $escape($errors['message']) ?></p><?php endif; ?>
        </div>
        <div class="form-field form-field-checkbox">
          <label><input id="privacy-acknowledged" name="privacy_acknowledged" type="checkbox" value="1" required <?= isset($errors['privacy_acknowledged']) ? 'aria-invalid="true" aria-describedby="privacy-error"' : '' ?>> I have read the <a href="/privacy/">privacy notice</a>. <span aria-hidden="true">(required)</span></label>
          <?php if (isset($errors['privacy_acknowledged'])): ?><p class="field-error" id="privacy-error"><?= $escape($errors['privacy_acknowledged']) ?></p><?php endif; ?>
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
  <footer>
    <p>Melanie Watsham trading as Stronger at Home Physiotherapy</p>
    <nav aria-label="Footer"><a href="/privacy/">Privacy</a><a href="/accessibility/">Accessibility</a></nav>
  </footer>
</body>
</html>
