<?php
declare(strict_types=1);
// Copy outside the public root, with permission 0600. Never commit real credentials.
return [
    'environment' => 'staging',
    'origin' => 'https://staging.stronger-at-home.co.uk',
    'username' => 'melanie',
    'password_hash' => '',
    'directory' => '/absolute/private/environment-specific/feedback',
];
