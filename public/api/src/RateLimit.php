<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

interface RateLimit
{
    public function allow(string $clientAddress, int $now): bool;
}
