<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

use StrongerAtHome\Enquiry\FileRateLimiter;

$directory = sys_get_temp_dir() . '/sah-rate-' . bin2hex(random_bytes(6));
$limiter = new FileRateLimiter($directory, 'test-hmac-key', 2, 3600);

assert_true($limiter->allow('192.0.2.10', 1000), 'first allowed');
assert_true($limiter->allow('192.0.2.10', 1001), 'second allowed');
assert_true(!$limiter->allow('192.0.2.10', 1002), 'third blocked');
assert_true($limiter->allow('192.0.2.10', 4601), 'expired window resets');

$counterFiles = glob($directory . '/*.json');
assert_true(is_array($counterFiles), 'counter directory can be inspected');
assert_same(1, count($counterFiles), 'one opaque counter is stored per client');
assert_true(!str_contains(basename($counterFiles[0]), '192.0.2.10'), 'counter filename does not expose client address');
$state = file_get_contents($counterFiles[0]);
assert_true(is_string($state), 'counter state can be read');
assert_true(!str_contains($state, '192.0.2.10'), 'counter state does not expose client address');
assert_same(0700, fileperms($directory) & 0777, 'counter directory has owner-only permissions');
assert_same(0600, fileperms($counterFiles[0]) & 0777, 'counter file has owner-only permissions');

file_put_contents($counterFiles[0], json_encode([
    'window_started' => 5000,
    'count' => 0,
    'unexpected_contact_data' => 'alex@example.com',
]));
assert_true($limiter->allow('192.0.2.10', 5001), 'valid counter with unexpected keys remains usable');
$normalisedState = json_decode((string) file_get_contents($counterFiles[0]), true);
assert_same(['window_started', 'count'], array_keys($normalisedState), 'counter writes discard all unexpected data');

$counterPath = static function (string $clientAddress) use ($directory): string {
    return $directory . '/' . hash_hmac('sha256', $clientAddress, 'test-hmac-key') . '.json';
};

$emptyStatePath = $counterPath('192.0.2.11');
touch($emptyStatePath);
chmod($emptyStatePath, 0600);
assert_true(!$limiter->allow('192.0.2.11', 5001), 'existing empty counter fails closed');

$malformedStatePath = $counterPath('192.0.2.12');
file_put_contents($malformedStatePath, 'not-json');
chmod($malformedStatePath, 0600);
assert_true(!$limiter->allow('192.0.2.12', 5001), 'existing malformed counter fails closed');

$truncatedStatePath = $counterPath('192.0.2.13');
file_put_contents($truncatedStatePath, '{"window_started":5000,"count":');
chmod($truncatedStatePath, 0600);
assert_true(!$limiter->allow('192.0.2.13', 5001), 'existing truncated counter fails closed');

$expiredStatePath = $counterPath('192.0.2.14');
file_put_contents($expiredStatePath, json_encode(['window_started' => 1000, 'count' => 2]));
chmod($expiredStatePath, 0600);
assert_true($limiter->allow('192.0.2.14', 4600), 'existing valid expired counter resets');
$expiredState = json_decode((string) file_get_contents($expiredStatePath), true);
assert_same(['window_started' => 4600, 'count' => 1], $expiredState, 'expired reset writes a fresh bounded window');

$unopenableStatePath = $counterPath('192.0.2.15');
mkdir($unopenableStatePath, 0700);
assert_true(!$limiter->allow('192.0.2.15', 5001), 'existing state that cannot be opened fails closed');
rmdir($unopenableStatePath);

foreach (glob($directory . '/*.json') ?: [] as $counterFile) {
    unlink($counterFile);
}
rmdir($directory);
