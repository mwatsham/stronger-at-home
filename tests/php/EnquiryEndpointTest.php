<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

$projectRoot = dirname(__DIR__, 2);
$entryPoint = $projectRoot . '/site/api/enquiry.php';
$temporaryDirectory = sys_get_temp_dir() . '/sah-endpoint-' . bin2hex(random_bytes(6));
mkdir($temporaryDirectory, 0700, true);
mkdir($temporaryDirectory . '/sessions', 0700);

/**
 * @param array<string, mixed> $config
 */
function endpoint_status(
    array $config,
    string $label,
    string $entryPoint,
    string $temporaryDirectory,
    bool $throwFromConfig = false,
    ?string $autoloadPath = null,
    bool $relativeConfigPath = false,
): int
{
    $safeLabel = preg_replace('/[^a-z0-9]+/', '-', strtolower($label));
    assert_true(is_string($safeLabel), $label . ' fixture label is valid');
    $configPath = $temporaryDirectory . '/' . $safeLabel . '-config.php';
    $runnerPath = $temporaryDirectory . '/' . $safeLabel . '-runner.php';
    $autoloadPath ??= dirname($entryPoint, 3) . '/vendor/autoload.php';
    $configEnvironmentPath = $relativeConfigPath ? basename($configPath) : $configPath;
    $configSource = $throwFromConfig
        ? "<?php\nthrow new RuntimeException('private configuration detail');\n"
        : "<?php\nreturn " . var_export($config, true) . ";\n";
    file_put_contents($configPath, $configSource);
    file_put_contents(
        $runnerPath,
        "<?php\n"
        . 'session_save_path(' . var_export($temporaryDirectory . '/sessions', true) . ");\n"
        . 'putenv(' . var_export('STRONGER_HOME_AUTOLOAD=' . $autoloadPath, true) . ");\n"
        . 'putenv(' . var_export('STRONGER_HOME_CONFIG=' . $configEnvironmentPath, true) . ");\n"
        . "\$_SERVER = ['REQUEST_METHOD' => 'GET'];\n"
        . "\$_POST = [];\n"
        . "register_shutdown_function(static function (): void {\n"
        . "    \$status = http_response_code();\n"
        . "    echo is_int(\$status) ? \$status : 200;\n"
        . "});\n"
        . 'require ' . var_export($entryPoint, true) . ";\n",
    );

    $process = proc_open(
        [PHP_BINARY, $runnerPath],
        [1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
        $pipes,
        $temporaryDirectory,
    );
    assert_true(is_resource($process), $label . ' endpoint process starts');
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $exitCode = proc_close($process);

    assert_same(0, $exitCode, $label . ' endpoint process exits normally');
    assert_same('', $stderr, $label . ' endpoint emits no warning or private detail');
    assert_true(is_string($stdout) && preg_match('/\A[0-9]{3}\z/', $stdout) === 1, $label . ' endpoint returns an HTTP status');

    return (int) $stdout;
}

$validConfig = [
    'environment' => 'staging',
    'allowed_origin' => 'https://staging.stronger-at-home.co.uk',
    'recipient' => 'safe-recipient@example.test',
    'sender' => 'website@stronger-at-home.co.uk',
    'smtp_host' => 'smtp.example.test',
    'smtp_port' => 587,
    'smtp_username' => 'mailer@example.test',
    'smtp_password' => 'test-password',
    'smtp_encryption' => 'tls',
    'rate_limit_secret' => 'test-rate-secret',
    'rate_limit_directory' => $temporaryDirectory . '/rate-limit',
];

$missingAutoloadPath = $temporaryDirectory . '/missing-autoload.php';
$publicAutoloadPath = $projectRoot . '/site/api/test-autoload-' . bin2hex(random_bytes(6)) . '.php';
$relativeAutoloadPath = $temporaryDirectory . '/relative-autoload.php';
file_put_contents(
    $publicAutoloadPath,
    "<?php\nrequire " . var_export($projectRoot . '/vendor/autoload.php', true) . ";\n",
);
file_put_contents(
    $relativeAutoloadPath,
    "<?php\nrequire " . var_export($projectRoot . '/vendor/autoload.php', true) . ";\n",
);
register_shutdown_function(static function () use ($publicAutoloadPath, $relativeAutoloadPath): void {
    foreach ([$publicAutoloadPath, $relativeAutoloadPath] as $fixturePath) {
        if (is_file($fixturePath)) {
            unlink($fixturePath);
        }
    }
});
$externalAutoloaderStatuses = [
    endpoint_status(
        $validConfig,
        'missing external autoloader',
        $entryPoint,
        $temporaryDirectory,
        false,
        $missingAutoloadPath,
    ),
    endpoint_status(
        $validConfig,
        'public external autoloader',
        $entryPoint,
        $temporaryDirectory,
        false,
        $publicAutoloadPath,
    ),
];
unlink($publicAutoloadPath);
assert_same(
    [500, 500],
    $externalAutoloaderStatuses,
    'missing and public-root autoloaders return blank generic failures',
);

$relativePathStatuses = [
    endpoint_status(
        $validConfig,
        'relative autoloader path',
        $entryPoint,
        $temporaryDirectory,
        false,
        basename($relativeAutoloadPath),
    ),
    endpoint_status(
        $validConfig,
        'relative configuration path',
        $entryPoint,
        $temporaryDirectory,
        false,
        null,
        true,
    ),
];
unlink($relativeAutoloadPath);
assert_same(
    [500, 500],
    $relativePathStatuses,
    'relative dependency and configuration paths return blank generic failures',
);

$invalidEnvironments = [
    'missing environment' => null,
    'non-scalar environment' => ['staging'],
    'differently cased environment' => 'Production',
    'typo environment' => 'prodction',
    'unsupported environment' => 'development',
    'empty environment' => '',
];
foreach ($invalidEnvironments as $label => $environment) {
    $config = $validConfig;
    if ($environment === null) {
        unset($config['environment']);
    } else {
        $config['environment'] = $environment;
    }
    assert_same(500, endpoint_status($config, $label, $entryPoint, $temporaryDirectory), $label . ' is rejected before request handling');
}

assert_same(
    405,
    endpoint_status($validConfig, 'valid staging', $entryPoint, $temporaryDirectory),
    'staging with a safe configured recipient reaches request handling',
);

$liveRecipientOnStaging = $validConfig;
$liveRecipientOnStaging['recipient'] = '  MELANIE@stronger-at-home.co.uk ';
assert_same(
    500,
    endpoint_status($liveRecipientOnStaging, 'live recipient on staging', $entryPoint, $temporaryDirectory),
    'staging rejects Melanie live recipient after normalization',
);

$productionConfig = $validConfig;
$productionConfig['environment'] = 'production';
$productionConfig['recipient'] = 'melanie@stronger-at-home.co.uk';
assert_same(
    405,
    endpoint_status($productionConfig, 'valid production', $entryPoint, $temporaryDirectory),
    'production with Melanie as recipient reaches request handling',
);

$wrongProductionRecipient = $productionConfig;
$wrongProductionRecipient['recipient'] = 'safe-recipient@example.test';
assert_same(
    500,
    endpoint_status($wrongProductionRecipient, 'wrong production recipient', $entryPoint, $temporaryDirectory),
    'production rejects any other recipient',
);

$invalidTransportConfig = $validConfig;
$invalidTransportConfig['smtp_port'] = 0;
assert_same(
    500,
    endpoint_status($invalidTransportConfig, 'transport construction failure', $entryPoint, $temporaryDirectory),
    'transport construction failure returns a blank generic 500',
);

assert_same(
    500,
    endpoint_status($validConfig, 'config exception', $entryPoint, $temporaryDirectory, true),
    'configuration exception returns a blank generic 500',
);

$configSource = file_get_contents($projectRoot . '/config/site.example.php');
assert_true(is_string($configSource), 'configuration example can be read');
assert_true(str_contains($configSource, "'environment' => getenv('APP_ENV')"), 'configuration example reads explicit APP_ENV');
assert_true(!str_contains($configSource, "getenv('APP_ENV') ?: 'staging'"), 'configuration example does not silently default APP_ENV');

foreach (glob($temporaryDirectory . '/sessions/*') ?: [] as $sessionFile) {
    unlink($sessionFile);
}
foreach (glob($temporaryDirectory . '/*-config.php') ?: [] as $fixtureFile) {
    unlink($fixtureFile);
}
foreach (glob($temporaryDirectory . '/*-runner.php') ?: [] as $fixtureFile) {
    unlink($fixtureFile);
}
rmdir($temporaryDirectory . '/sessions');
rmdir($temporaryDirectory);
