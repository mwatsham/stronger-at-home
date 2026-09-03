<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

final class EnquiryMessage
{
    public function __construct(
        public readonly string $subject,
        public readonly string $textBody,
        public readonly string $htmlBody,
        public readonly string $replyToEmail,
        public readonly string $replyToName,
    ) {
    }

    /**
     * @param array<string, mixed> $data
     */
    public static function from(array $data): self
    {
        $name = self::value($data, 'name');
        $email = self::value($data, 'email');
        $labels = [
            'Name' => $name,
            'Email' => $email,
            'Phone' => self::value($data, 'phone'),
            'Preferred contact' => self::value($data, 'preferred_contact'),
            'Postcode' => self::value($data, 'postcode'),
            'Enquiry' => self::value($data, 'message'),
        ];

        $text = implode("\n", array_map(
            static fn(string $label, string $value): string => $label . ': ' . $value,
            array_keys($labels),
            array_values($labels),
        ));
        $rows = implode('', array_map(
            static fn(string $label, string $value): string => '<tr><th scope="row">' . self::escape($label) . '</th><td>' . nl2br(self::escape($value)) . '</td></tr>',
            array_keys($labels),
            array_values($labels),
        ));

        return new self(
            'New website appointment request',
            $text,
            '<table>' . $rows . '</table>',
            self::safeReplyToEmail($email),
            self::safeReplyToName($name),
        );
    }

    /**
     * @param array<string, mixed> $data
     */
    private static function value(array $data, string $key): string
    {
        $value = $data[$key] ?? '';

        if (!is_string($value) || preg_match('//u', $value) !== 1) {
            return '';
        }

        return $value;
    }

    private static function safeReplyToEmail(string $email): string
    {
        if (preg_match('/[\r\n]/', $email) === 1 || filter_var($email, FILTER_VALIDATE_EMAIL) === false) {
            return '';
        }

        return $email;
    }

    private static function safeReplyToName(string $name): string
    {
        return str_replace(["\r", "\n"], '', $name);
    }

    private static function escape(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
