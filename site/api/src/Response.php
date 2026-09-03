<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

final class Response
{
    /**
     * @param array<string, string> $headers
     * @param array<string, mixed> $flash
     */
    public function __construct(
        public readonly int $status,
        public readonly array $headers = [],
        public readonly array $flash = [],
    ) {
    }
}
