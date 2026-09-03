<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

use StrongerAtHome\Enquiry\EnquiryController;
use StrongerAtHome\Enquiry\EnquiryMessage;
use StrongerAtHome\Enquiry\EnquiryValidator;
use StrongerAtHome\Enquiry\MailTransport;
use StrongerAtHome\Enquiry\PhpMailerTransport;
use StrongerAtHome\Enquiry\RateLimit;

final class FakeMailTransport implements MailTransport
{
    /** @var list<EnquiryMessage> */
    public array $sent = [];
    public bool $fail = false;

    public function send(EnquiryMessage $message): void
    {
        if ($this->fail) {
            throw new RuntimeException('simulated provider failure containing private details');
        }
        $this->sent[] = $message;
    }
}

final class FakeRateLimit implements RateLimit
{
    public int $calls = 0;
    public string $lastClientAddress = '';

    public function __construct(private bool $allowed)
    {
    }

    public function allow(string $clientAddress, int $now): bool
    {
        $this->calls++;
        $this->lastClientAddress = $clientAddress;
        return $this->allowed;
    }
}

/**
 * @return array{0: EnquiryController, 1: FakeMailTransport, 2: FakeRateLimit}
 */
function controller_with(bool $rateAllowed = true): array
{
    $transport = new FakeMailTransport();
    $rateLimit = new FakeRateLimit($rateAllowed);
    $controller = new EnquiryController(
        new EnquiryValidator(),
        $transport,
        $rateLimit,
        'https://staging.stronger-at-home.co.uk',
    );

    return [$controller, $transport, $rateLimit];
}

$server = [
    'REQUEST_METHOD' => 'POST',
    'HTTP_ORIGIN' => 'https://staging.stronger-at-home.co.uk',
    'REMOTE_ADDR' => '192.0.2.10',
];
$post = [
    'name' => 'Alex Morgan',
    'email' => 'alex@example.com',
    'phone' => '',
    'preferred_contact' => 'email',
    'postcode' => 'KT17 4LZ',
    'message' => 'Please contact me about an assessment.',
    'privacy_acknowledged' => '1',
    'website' => '',
    'csrf_token' => 'known-token',
];
$session = ['csrf_token' => 'known-token'];

[$controller, $transport, $rateLimit] = controller_with();
$response = $controller->handle($server, $post, $session);
assert_same(303, $response->status, 'success redirects');
assert_same('/contact/?sent=1#form-feedback', $response->headers['Location'], 'success target');
assert_same(['kind' => 'success'], $response->flash, 'success sets generic flash state');
assert_same(1, count($transport->sent), 'one message sent');
assert_same('192.0.2.10', $rateLimit->lastClientAddress, 'rate limiter receives the client address');
assert_true(!str_contains($transport->sent[0]->textBody, 'known-token'), 'CSRF token is not passed into the message');

[$controller, $transport] = controller_with();
$getResponse = $controller->handle(['REQUEST_METHOD' => 'GET'], [], []);
assert_same(405, $getResponse->status, 'GET is rejected');
assert_same('POST', $getResponse->headers['Allow'], 'GET response advertises POST');
assert_same(0, count($transport->sent), 'GET does not send mail');

[$controller, $transport] = controller_with();
$wrongOrigin = $server;
$wrongOrigin['HTTP_ORIGIN'] = 'https://attacker.example';
assert_same(403, $controller->handle($wrongOrigin, $post, $session)->status, 'disallowed origin is rejected');
$nonScalarOrigin = $server;
$nonScalarOrigin['HTTP_ORIGIN'] = ['https://staging.stronger-at-home.co.uk'];
assert_same(403, $controller->handle($nonScalarOrigin, $post, $session)->status, 'non-scalar origin is rejected');
assert_same(0, count($transport->sent), 'invalid origins do not send mail');

$csrfCases = [
    'missing submitted CSRF token' => [$session, array_diff_key($post, ['csrf_token' => true])],
    'missing session CSRF token' => [[], $post],
    'non-scalar submitted CSRF token' => [$session, array_merge($post, ['csrf_token' => ['known-token']])],
    'non-scalar session CSRF token' => [['csrf_token' => ['known-token']], $post],
    'malformed submitted CSRF token' => [['csrf_token' => "bad\r\ntoken"], array_merge($post, ['csrf_token' => "bad\r\ntoken"])],
    'oversized submitted CSRF token' => [['csrf_token' => str_repeat('a', 129)], array_merge($post, ['csrf_token' => str_repeat('a', 129)])],
    'mismatched submitted CSRF token' => [$session, array_merge($post, ['csrf_token' => 'different-token'])],
];
foreach ($csrfCases as $label => [$caseSession, $casePost]) {
    [$controller, $transport, $caseRateLimit] = controller_with();
    $response = $controller->handle($server, $casePost, $caseSession);
    assert_same(403, $response->status, $label . ' is rejected');
    assert_same(0, count($transport->sent), $label . ' does not send mail');
    assert_same(0, $caseRateLimit->calls, $label . ' does not consume rate allowance');
}

[$controller, $transport] = controller_with();
$controller->handle($server, $post, $session);
$replayResponse = $controller->handle($server, $post, []);
assert_same(403, $replayResponse->status, 'a token removed after its valid use cannot be replayed');
assert_same(1, count($transport->sent), 'replay does not send a duplicate message');

[$controller, $transport, $honeypotRateLimit] = controller_with();
$honeypotPost = $post;
$honeypotPost['website'] = 'bot.example';
unset($honeypotPost['csrf_token']);
$honeypotResponse = $controller->handle($server, $honeypotPost, []);
assert_same(303, $honeypotResponse->status, 'honeypot receives a silent redirect');
assert_same('/contact/?sent=1#form-feedback', $honeypotResponse->headers['Location'], 'honeypot receives the success target');
assert_same([], $honeypotResponse->flash, 'honeypot receives no visible success state');
assert_same(0, count($transport->sent), 'honeypot does not send mail');
assert_same(0, $honeypotRateLimit->calls, 'honeypot does not consume rate allowance');

[$controller, $transport] = controller_with();
$invalidPost = $post;
$invalidPost['name'] = '<script>alert(1)</script>';
$invalidPost['email'] = 'not-an-email';
$invalidPost['message'] = 'short';
$invalidResponse = $controller->handle($server, $invalidPost, $session);
assert_same(303, $invalidResponse->status, 'validation failure redirects');
assert_same('/contact/?error=validation#form-feedback', $invalidResponse->headers['Location'], 'validation failure target');
assert_same('validation', $invalidResponse->flash['kind'], 'validation failure sets generic kind');
assert_true(isset($invalidResponse->flash['errors']['email']), 'validation failure returns field feedback');
assert_same(
    ['name', 'email', 'phone', 'preferred_contact', 'postcode'],
    array_keys($invalidResponse->flash['values']),
    'only approved low-sensitivity values are preserved',
);
assert_true(!isset($invalidResponse->flash['values']['message']), 'message is never preserved');
assert_true(!isset($invalidResponse->flash['values']['csrf_token']), 'CSRF token is never preserved');
assert_same(0, count($transport->sent), 'invalid fields do not send mail');

[$controller] = controller_with();
$oversizedPost = $post;
$oversizedPost['name'] = str_repeat('x', 10000);
$oversizedResponse = $controller->handle($server, $oversizedPost, $session);
assert_same('', $oversizedResponse->flash['values']['name'], 'oversized invalid values are not stored in session flash');

[$controller, $transport] = controller_with(false);
$rateResponse = $controller->handle($server, $post, $session);
assert_same(303, $rateResponse->status, 'rate limit redirects');
assert_same('/contact/?error=rate#form-feedback', $rateResponse->headers['Location'], 'rate-limit target');
assert_same(['kind' => 'rate'], $rateResponse->flash, 'rate limit has generic flash state only');
assert_same(0, count($transport->sent), 'rate limit does not send mail');

[$controller, $transport] = controller_with();
$transport->fail = true;
$deliveryResponse = $controller->handle($server, $post, $session);
assert_same(303, $deliveryResponse->status, 'delivery failure redirects');
assert_same('/contact/?error=delivery#form-feedback', $deliveryResponse->headers['Location'], 'delivery failure target');
assert_same('delivery', $deliveryResponse->flash['kind'], 'delivery failure is generic');
assert_true(!isset($deliveryResponse->flash['errors']), 'delivery failure exposes no provider details');
assert_true(!isset($deliveryResponse->flash['values']['message']), 'delivery failure never preserves the message');

final class FakePhpMailer extends PHPMailer\PHPMailer\PHPMailer
{
    public bool $fail = false;

    public function send(): bool
    {
        if ($this->fail) {
            throw new PHPMailer\PHPMailer\Exception('provider error containing a credential');
        }

        return true;
    }
}

$mailConfig = [
    'smtp_host' => 'smtp.example.test',
    'smtp_port' => 587,
    'smtp_username' => 'mailer@example.test',
    'smtp_password' => 'test-password',
    'smtp_encryption' => 'tls',
    'sender' => 'website@stronger-at-home.co.uk',
    'recipient' => 'melanie@stronger-at-home.co.uk',
];
$fakeMailer = new FakePhpMailer(true);
$mailTransport = new PhpMailerTransport($mailConfig, static fn(): FakePhpMailer => $fakeMailer);
$mailTransport->send(EnquiryMessage::from($post));
assert_same('smtp', $fakeMailer->Mailer, 'PHPMailer is configured for SMTP');
assert_true($fakeMailer->SMTPAuth, 'SMTP authentication is enabled');
assert_same('smtp.example.test', $fakeMailer->Host, 'SMTP host comes from configuration');
assert_same('mailer@example.test', $fakeMailer->Username, 'SMTP username comes from configuration');
assert_same('test-password', $fakeMailer->Password, 'SMTP password comes from configuration');
assert_same('tls', $fakeMailer->SMTPSecure, 'SMTP encryption comes from configuration');
assert_same(587, $fakeMailer->Port, 'SMTP port comes from configuration');
assert_same(0, $fakeMailer->SMTPDebug, 'SMTP debug output is disabled');
assert_same('UTF-8', $fakeMailer->CharSet, 'mail uses UTF-8');
assert_same('website@stronger-at-home.co.uk', $fakeMailer->From, 'sender is deployment configured');
assert_same('Stronger at Home Physiotherapy', $fakeMailer->FromName, 'sender uses the business name');
assert_same('melanie@stronger-at-home.co.uk', $fakeMailer->getToAddresses()[0][0], 'recipient is deployment configured');
assert_same('alex@example.com', $fakeMailer->getReplyToAddresses()[0][0], 'validated email is reply-to');
assert_same('text/html', $fakeMailer->ContentType, 'message has an HTML body');

$fakeMailer = new FakePhpMailer(true);
$fakeMailer->fail = true;
$mailTransport = new PhpMailerTransport($mailConfig, static fn(): FakePhpMailer => $fakeMailer);
$genericFailure = null;
try {
    $mailTransport->send(EnquiryMessage::from($post));
} catch (RuntimeException $exception) {
    $genericFailure = $exception;
}
assert_true($genericFailure instanceof RuntimeException, 'provider failure becomes a delivery exception');
assert_same('Unable to deliver enquiry.', $genericFailure->getMessage(), 'delivery exception is generic');
assert_same(null, $genericFailure->getPrevious(), 'provider details are not chained into the delivery exception');

$invalidMailConfig = $mailConfig;
$invalidMailConfig['smtp_password'] = '';
$configurationRejected = false;
try {
    new PhpMailerTransport($invalidMailConfig);
} catch (InvalidArgumentException) {
    $configurationRejected = true;
}
assert_true($configurationRejected, 'empty SMTP credentials are rejected');

$projectRoot = dirname(__DIR__, 2);
$exampleConfigPath = $projectRoot . '/config/site.example.php';
$entryPointPath = $projectRoot . '/site/api/enquiry.php';
assert_true(is_file($exampleConfigPath), 'non-secret configuration contract exists');
assert_true(is_file($entryPointPath), 'HTTP entry point exists');

$configSource = file_get_contents($exampleConfigPath);
assert_true(is_string($configSource), 'configuration contract can be read');
foreach (['SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'RATE_LIMIT_SECRET', 'RATE_LIMIT_DIRECTORY'] as $environmentName) {
    assert_true(str_contains($configSource, $environmentName), $environmentName . ' is deployment configured');
}

$entryPointSource = file_get_contents($entryPointPath);
assert_true(is_string($entryPointSource), 'HTTP entry point can be read');
assert_true(str_contains($entryPointSource, "'secure' => true"), 'session cookie is Secure');
assert_true(str_contains($entryPointSource, "'httponly' => true"), 'session cookie is HttpOnly');
assert_true(str_contains($entryPointSource, "'samesite' => 'Lax'"), 'session cookie uses SameSite=Lax');
assert_true(str_contains($entryPointSource, "ini_set('session.use_strict_mode', '1')"), 'session strict mode is enabled');
assert_true(str_contains($entryPointSource, "ini_set('display_errors', '0')"), 'entry point suppresses diagnostic output');
assert_true(str_contains($entryPointSource, "unset(\$_SESSION['csrf_token'])"), 'accepted POST consumes its CSRF token');
assert_true(!str_contains($entryPointSource, 'error_log'), 'entry point does not log enquiry data');

$sessionDirectory = sys_get_temp_dir() . '/sah-session-' . bin2hex(random_bytes(6));
mkdir($sessionDirectory, 0700, true);
session_save_path($sessionDirectory);
session_id('sah-contact-render-test');
session_start();
$_SESSION['form_flash'] = [
    'kind' => 'validation',
    'errors' => [
        'name' => 'Please enter your name.',
        'email' => '<script>alert("error")</script>',
        'message' => 'Please enter a short enquiry.',
    ],
    'values' => [
        'name' => '<script>alert("name")</script>',
        'email' => 'alex@example.com',
        'phone' => '07123 456789',
        'preferred_contact' => 'phone',
        'postcode' => 'kt17 4lz',
        'message' => 'private message must not be rendered',
    ],
];
session_write_close();

ob_start();
include $projectRoot . '/site/contact/index.php';
$contactHtml = ob_get_clean();
assert_true(is_string($contactHtml), 'contact page renders');
assert_true(str_contains($contactHtml, '&lt;script&gt;alert(&quot;name&quot;)&lt;/script&gt;'), 'restored values are escaped');
assert_true(str_contains($contactHtml, '&lt;script&gt;alert(&quot;error&quot;)&lt;/script&gt;'), 'field feedback is escaped');
assert_true(!str_contains($contactHtml, '<script>alert("name")</script>'), 'restored values cannot inject markup');
assert_true(!str_contains($contactHtml, 'private message must not be rendered'), 'message is never restored');
assert_true(str_contains($contactHtml, 'aria-invalid="true"'), 'invalid fields are identified accessibly');
assert_true(str_contains($contactHtml, 'id="form-feedback"'), 'redirect fragment targets stable form feedback');
assert_true(str_contains($contactHtml, 'data-flash-kind="validation"'), 'rendered flash state exposes only its generic kind to focus handling');
assert_true(str_contains($contactHtml, 'value="phone" selected'), 'preferred contact is restored');
assert_true(preg_match('/name="csrf_token" type="hidden" value="[a-f0-9]{64}"/', $contactHtml) === 1, 'contact page renders a 32-byte CSRF token');
assert_true(!isset($_SESSION['form_flash']), 'flash state is consumed after one render');
assert_true(isset($_SESSION['csrf_token']) && is_string($_SESSION['csrf_token']), 'new CSRF token is stored in the session');

$siteScript = file_get_contents($projectRoot . '/site/assets/js/site.js');
assert_true(is_string($siteScript), 'site script can be read');
assert_true(str_contains($siteScript, "form.querySelector('[aria-invalid=\"true\"]')"), 'validation flash selects the first invalid field');
assert_true(str_contains($siteScript, 'feedbackTarget.focus()'), 'flash feedback receives programmatic focus');

session_write_close();
foreach (glob($sessionDirectory . '/*') ?: [] as $sessionFile) {
    unlink($sessionFile);
}
rmdir($sessionDirectory);
