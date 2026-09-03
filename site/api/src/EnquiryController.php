<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

final class EnquiryController
{
    public function __construct(
        private EnquiryValidator $validator,
        private MailTransport $transport,
        private RateLimit $rateLimit,
        private string $allowedOrigin,
    ) {
    }

    /**
     * @param array<string, mixed> $server
     * @param array<string, mixed> $post
     * @param array<string, mixed> $session
     */
    public function handle(array $server, array $post, array $session): Response
    {
        if ($this->stringValue($server, 'REQUEST_METHOD') !== 'POST') {
            return new Response(405, ['Allow' => 'POST']);
        }

        $origin = $this->stringValue($server, 'HTTP_ORIGIN');
        if ($origin === null || !hash_equals($this->allowedOrigin, $origin)) {
            return new Response(403);
        }

        if ($this->honeypotIsFilled($post)) {
            return new Response(303, ['Location' => '/contact/?sent=1#form-feedback']);
        }

        if (!$this->hasValidCsrfToken($post, $session)) {
            return new Response(403);
        }

        $clientAddress = $this->stringValue($server, 'REMOTE_ADDR') ?? '';
        if (!$this->rateLimit->allow($clientAddress, time())) {
            return new Response(
                303,
                ['Location' => '/contact/?error=rate#form-feedback'],
                ['kind' => 'rate'],
            );
        }

        $result = $this->validator->validate($post);
        $safeValues = $this->safeFlashValues($result->data);

        if (!$result->isValid()) {
            return new Response(
                303,
                ['Location' => '/contact/?error=validation#form-feedback'],
                ['kind' => 'validation', 'errors' => $result->errors, 'values' => $safeValues],
            );
        }

        try {
            $this->transport->send(EnquiryMessage::from($result->data));
        } catch (\Throwable) {
            return new Response(
                303,
                ['Location' => '/contact/?error=delivery#form-feedback'],
                ['kind' => 'delivery', 'values' => $safeValues],
            );
        }

        return new Response(
            303,
            ['Location' => '/contact/?sent=1#form-feedback'],
            ['kind' => 'success'],
        );
    }

    /**
     * @param array<string, mixed> $post
     */
    private function honeypotIsFilled(array $post): bool
    {
        if (!array_key_exists('website', $post)) {
            return false;
        }

        return !is_string($post['website']) || trim($post['website']) !== '';
    }

    /**
     * @param array<string, mixed> $post
     * @param array<string, mixed> $session
     */
    private function hasValidCsrfToken(array $post, array $session): bool
    {
        $submitted = $this->stringValue($post, 'csrf_token');
        $expected = $this->stringValue($session, 'csrf_token');

        if (!$this->isWellFormedCsrfToken($submitted) || !$this->isWellFormedCsrfToken($expected)) {
            return false;
        }

        return hash_equals($expected, $submitted);
    }

    private function isWellFormedCsrfToken(?string $token): bool
    {
        return $token !== null
            && $token !== ''
            && strlen($token) <= 128
            && preg_match('/\A[A-Za-z0-9_-]+\z/D', $token) === 1;
    }

    /**
     * @param array<string, mixed> $data
     * @return array<string, string>
     */
    private function safeFlashValues(array $data): array
    {
        $maximumLengths = [
            'name' => 100,
            'email' => 254,
            'phone' => 30,
            'preferred_contact' => 5,
            'postcode' => 10,
        ];
        $values = [];
        foreach ($maximumLengths as $key => $maximumLength) {
            $value = $data[$key] ?? '';
            $values[$key] = is_string($value)
                && strlen($value) <= $maximumLength
                && preg_match('//u', $value) === 1
                    ? $value
                    : '';
        }

        return $values;
    }

    /**
     * @param array<string, mixed> $values
     */
    private function stringValue(array $values, string $key): ?string
    {
        $value = $values[$key] ?? null;

        return is_string($value) ? $value : null;
    }
}
