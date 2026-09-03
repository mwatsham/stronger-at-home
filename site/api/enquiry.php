<?php
declare(strict_types=1);

use StrongerAtHome\Enquiry\EnquiryController;
use StrongerAtHome\Enquiry\EnquiryValidator;
use StrongerAtHome\Enquiry\FileRateLimiter;
use StrongerAtHome\Enquiry\PhpMailerTransport;

ini_set('display_errors', '0');

try {
$autoloadPath = dirname(__DIR__, 2) . '/vendor/autoload.php';
if (!is_file($autoloadPath) || !is_readable($autoloadPath)) {
    http_response_code(500);
    exit;
}
require $autoloadPath;

$publicRoot = realpath(dirname(__DIR__));
$configPath = getenv('STRONGER_HOME_CONFIG') ?: dirname(__DIR__, 2) . '/config/site.php';
$resolvedConfigPath = realpath($configPath);
if ($publicRoot === false
    || $resolvedConfigPath === false
    || $resolvedConfigPath === $publicRoot
    || str_starts_with($resolvedConfigPath, $publicRoot . DIRECTORY_SEPARATOR)
) {
    http_response_code(500);
    exit;
}

$config = require $resolvedConfigPath;
if (!is_array($config)) {
    http_response_code(500);
    exit;
}

foreach (['environment', 'allowed_origin', 'recipient', 'sender', 'smtp_host', 'smtp_username', 'smtp_password', 'rate_limit_secret', 'rate_limit_directory'] as $requiredKey) {
    if (!isset($config[$requiredKey]) || !is_string($config[$requiredKey]) || trim($config[$requiredKey]) === '') {
        http_response_code(500);
        exit;
    }
}
if (!in_array($config['environment'], ['staging', 'production'], true)) {
    http_response_code(500);
    exit;
}

$originParts = parse_url($config['allowed_origin']);
if (!is_array($originParts)
    || ($originParts['scheme'] ?? '') !== 'https'
    || !isset($originParts['host'])
    || isset($originParts['user'])
    || isset($originParts['pass'])
    || isset($originParts['query'])
    || isset($originParts['fragment'])
    || (($originParts['path'] ?? '') !== '')
) {
    http_response_code(500);
    exit;
}

$rateLimitParent = realpath(dirname($config['rate_limit_directory']));
if (!str_starts_with($config['rate_limit_directory'], DIRECTORY_SEPARATOR) || $rateLimitParent === false) {
    http_response_code(500);
    exit;
}
$rateLimitDirectory = $rateLimitParent . DIRECTORY_SEPARATOR . basename($config['rate_limit_directory']);
if ($rateLimitDirectory === $publicRoot || str_starts_with($rateLimitDirectory, $publicRoot . DIRECTORY_SEPARATOR)) {
    http_response_code(500);
    exit;
}
$config['rate_limit_directory'] = $rateLimitDirectory;

$recipient = strtolower(trim($config['recipient']));
if (($config['environment'] === 'production' && $recipient !== 'melanie@stronger-at-home.co.uk')
    || ($config['environment'] === 'staging' && $recipient === 'melanie@stronger-at-home.co.uk')
) {
    http_response_code(500);
    exit;
}

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

$controller = new EnquiryController(
    new EnquiryValidator(),
    new PhpMailerTransport($config),
    new FileRateLimiter(
        $config['rate_limit_directory'],
        $config['rate_limit_secret'],
        5,
        3600,
    ),
    $config['allowed_origin'],
);
$response = $controller->handle($_SERVER, $_POST, $_SESSION);

unset($_SESSION['form_flash']);
if ($response->flash !== []) {
    $_SESSION['form_flash'] = $response->flash;
}
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    unset($_SESSION['csrf_token']);
}
session_write_close();

http_response_code($response->status);
foreach ($response->headers as $name => $value) {
    header($name . ': ' . $value);
}
exit;
} catch (\Throwable) {
    if (session_status() === PHP_SESSION_ACTIVE) {
        session_write_close();
    }
    http_response_code(500);
    exit;
}
