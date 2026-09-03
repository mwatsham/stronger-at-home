<?php
declare(strict_types=1);

return [
    'environment' => getenv('APP_ENV') ?: 'staging',
    'allowed_origin' => getenv('ALLOWED_ORIGIN') ?: 'https://staging.stronger-at-home.co.uk',
    'recipient' => getenv('ENQUIRY_RECIPIENT') ?: '',
    'sender' => getenv('ENQUIRY_SENDER') ?: '',
    'smtp_host' => getenv('SMTP_HOST') ?: '',
    'smtp_port' => (int) (getenv('SMTP_PORT') ?: 587),
    'smtp_username' => getenv('SMTP_USERNAME') ?: '',
    'smtp_password' => getenv('SMTP_PASSWORD') ?: '',
    'smtp_encryption' => getenv('SMTP_ENCRYPTION') ?: 'tls',
    'rate_limit_secret' => getenv('RATE_LIMIT_SECRET') ?: '',
    'rate_limit_directory' => getenv('RATE_LIMIT_DIRECTORY') ?: '',
];
