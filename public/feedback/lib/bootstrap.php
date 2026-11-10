<?php
declare(strict_types=1);
require_once __DIR__ . '/FeedbackStore.php';

function feedbackConfig(): array
{
    $path = getenv('STRONGER_HOME_FEEDBACK_CONFIG');
    $public = realpath(dirname(__DIR__, 2));
    if (!is_string($path) || realpath($path) !== $path || !is_file($path)
        || is_link($path) || (fileperms($path) & 0077) !== 0
        || str_starts_with($path, $public . '/')) throw new RuntimeException('Feedback is not configured.');
    $c = require $path;
    if (!is_array($c) || !in_array($c['environment'] ?? '', ['local','staging','production'],true)
        || ($c['username'] ?? '') !== 'melanie' || !is_string($c['password_hash'] ?? null)
        || (password_get_info($c['password_hash'])['algoName'] ?? 'unknown') === 'unknown'
        || !is_string($c['directory'] ?? null) || !is_string($c['origin'] ?? null)) throw new RuntimeException('Invalid feedback configuration.');
    $directory = realpath($c['directory']);
    if ($directory === false || $directory !== $c['directory'] || $directory === $public
        || str_starts_with($directory, $public . '/')) throw new RuntimeException('Invalid private directory.');
    $local = $c['environment'] === 'local';
    $expected = $c['environment'] === 'staging' ? 'https://staging.stronger-at-home.co.uk' : 'https://stronger-at-home.co.uk';
    if ($local) {
        if (!preg_match('~\Ahttp://127\.0\.0\.1:[0-9]{2,5}\z~', $c['origin'])
            || !in_array($_SERVER['REMOTE_ADDR'] ?? '', ['127.0.0.1','::1'],true)) throw new RuntimeException('Local preview requires loopback.');
    } elseif ($c['origin'] !== $expected || ($_SERVER['HTTPS'] ?? '') !== 'on') {
        throw new RuntimeException('HTTPS is required.');
    }
    $host = parse_url($c['origin'], PHP_URL_HOST);
    $port = parse_url($c['origin'], PHP_URL_PORT);
    if (($_SERVER['HTTP_HOST'] ?? '') !== $host . ($port ? ':' . $port : '')) throw new RuntimeException('Unexpected host.');
    return $c;
}

function feedbackHeaders(): void
{
    header('Cache-Control: no-store, max-age=0');
    header('X-Robots-Tag: noindex, nofollow');
    header('X-Content-Type-Options: nosniff');
    // Keep Origin on same-origin form POSTs; disclose no referrer off-site.
    header('Referrer-Policy: same-origin');
    header("Content-Security-Policy: default-src 'self'; style-src 'self'; script-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'");
}
