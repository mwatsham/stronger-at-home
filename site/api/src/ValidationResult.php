<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

final class ValidationResult
{
    /**
     * @param array<string, string> $data
     * @param array<string, string> $errors
     */
    public function __construct(
        public readonly array $data,
        public readonly array $errors,
    ) {
    }

    public function isValid(): bool
    {
        return $this->errors === [];
    }
}
