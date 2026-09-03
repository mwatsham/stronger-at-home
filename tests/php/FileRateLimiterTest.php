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

$cleanupDirectory = sys_get_temp_dir() . '/sah-rate-cleanup-' . bin2hex(random_bytes(6));
mkdir($cleanupDirectory, 0700, true);
for ($index = 0; $index < 25; $index++) {
    $stalePath = $cleanupDirectory . '/' . hash('sha256', 'stale-' . $index) . '.json';
    file_put_contents($stalePath, json_encode(['window_started' => 1, 'count' => 1]));
    chmod($stalePath, 0600);
    touch($stalePath, 1);
}
$cleanupLimiter = new FileRateLimiter($cleanupDirectory, 'cleanup-key', 2, 3600);
assert_true($cleanupLimiter->allow('198.51.100.1', 100000), 'cleanup request is accepted');
assert_true($cleanupLimiter->allow('198.51.100.1', 100001), 'second cleanup request is accepted');
$remainingCleanupFiles = glob($cleanupDirectory . '/*.json');
assert_true(is_array($remainingCleanupFiles), 'cleaned counter directory can be inspected');
assert_same(1, count($remainingCleanupFiles), 'deterministic cursor eventually removes more than one cleanup batch');

$capacityDirectory = sys_get_temp_dir() . '/sah-rate-capacity-' . bin2hex(random_bytes(6));
mkdir($capacityDirectory, 0700, true);
$capacity = (new ReflectionClass(FileRateLimiter::class))->getConstant('MAXIMUM_COUNTER_FILES');
assert_true(is_int($capacity) && $capacity > 20, 'counter capacity is a fixed positive bound above the cleanup batch');
for ($index = 0; $index < $capacity; $index++) {
    $capacityPath = $capacityDirectory . '/' . hash('sha256', 'capacity-' . $index) . '.json';
    file_put_contents($capacityPath, json_encode(['window_started' => 5000, 'count' => 1]));
    chmod($capacityPath, 0600);
}
$capacityLimiter = new FileRateLimiter($capacityDirectory, 'capacity-key', 2, 3600);
assert_true(!$capacityLimiter->allow('203.0.113.200', 5001), 'new unique client fails closed at counter capacity');
$capacityFiles = glob($capacityDirectory . '/*.json');
assert_true(is_array($capacityFiles), 'capacity directory can be inspected');
assert_same($capacity, count($capacityFiles), 'counter file count cannot grow past the hard capacity');

foreach ([$directory, $cleanupDirectory, $capacityDirectory] as $testDirectory) {
    foreach (new FilesystemIterator($testDirectory, FilesystemIterator::SKIP_DOTS) as $entry) {
        unlink($entry->getPathname());
    }
    rmdir($testDirectory);
}
