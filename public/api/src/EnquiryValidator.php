<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

final class EnquiryValidator
{
    /**
     * @param array<string, mixed> $input
     */
    public function validate(array $input): ValidationResult
    {
        $fields = [];
        foreach (['name', 'email', 'phone', 'preferred_contact', 'postcode', 'message', 'privacy_acknowledged', 'website'] as $field) {
            $fields[$field] = $this->readField($input, $field);
        }

        $data = [
            'name' => trim($fields['name']['value']),
            'email' => trim($fields['email']['value']),
            'phone' => trim($fields['phone']['value']),
            'preferred_contact' => $fields['preferred_contact']['value'],
            'postcode' => strtoupper((string) preg_replace('/\s+/', ' ', trim($fields['postcode']['value']))),
            'message' => trim($fields['message']['value']),
            'privacy_acknowledged' => $fields['privacy_acknowledged']['value'],
        ];
        $errors = [];

        if (!$fields['name']['valid'] || strlen($data['name']) < 2 || strlen($data['name']) > 100 || $this->hasHeaderControls($data['name'])) {
            $errors['name'] = 'Please enter your name.';
        }
        if (!$fields['preferred_contact']['valid'] || !in_array($data['preferred_contact'], ['email', 'phone'], true)) {
            $errors['preferred_contact'] = 'Please choose email or phone.';
        }
        if (!$fields['email']['valid'] || ($data['email'] !== '' && (strlen($data['email']) > 254 || filter_var($data['email'], FILTER_VALIDATE_EMAIL) === false))) {
            $errors['email'] = 'Please enter a valid email address.';
        }
        if ($data['preferred_contact'] === 'email' && $data['email'] === '') {
            $errors['email'] = 'Please provide an email address.';
        }
        if (!$fields['phone']['valid'] || ($data['phone'] !== '' && !$this->isValidPhone($data['phone']))) {
            $errors['phone'] = 'Please enter a valid phone number.';
        }
        if ($data['preferred_contact'] === 'phone' && $fields['phone']['valid'] && $data['phone'] === '') {
            $errors['phone'] = 'Please provide a phone number.';
        }
        if (!$fields['postcode']['valid'] || !$this->isUkPostcode($data['postcode'])) {
            $errors['postcode'] = 'Please enter a UK postcode.';
        }
        if (!$fields['message']['valid'] || strlen($data['message']) < 10 || strlen($data['message']) > 1000) {
            $errors['message'] = 'Please enter a short enquiry between 10 and 1000 characters.';
        }
        if (!$fields['privacy_acknowledged']['valid'] || $data['privacy_acknowledged'] !== '1') {
            $errors['privacy_acknowledged'] = 'Please confirm that you have read the privacy notice.';
        }
        if (!$fields['website']['valid'] || trim($fields['website']['value']) !== '') {
            $errors['website'] = 'Invalid submission.';
        }

        return new ValidationResult($data, $errors);
    }

    /**
     * @param array<string, mixed> $input
     * @return array{value: string, valid: bool}
     */
    private function readField(array $input, string $field): array
    {
        if (!array_key_exists($field, $input)) {
            return ['value' => '', 'valid' => true];
        }

        $value = $input[$field];
        if (!is_string($value) || preg_match('//u', $value) !== 1) {
            return ['value' => '', 'valid' => false];
        }

        return ['value' => $value, 'valid' => true];
    }

    private function hasHeaderControls(string $value): bool
    {
        return preg_match('/[\r\n]/', $value) === 1;
    }

    private function isValidPhone(string $phone): bool
    {
        if (preg_match('/^\+?[0-9() .-]{7,30}$/', $phone) !== 1) {
            return false;
        }

        $digits = preg_replace('/\D/', '', $phone);

        return is_string($digits) && strlen($digits) >= 7 && strlen($digits) <= 15;
    }

    private function isUkPostcode(string $postcode): bool
    {
        return preg_match(
            '/^(?:GIR ?0AA|(?:[A-PR-UWYZ][0-9]{1,2}|[A-PR-UWYZ][A-HK-Y][0-9]{1,2}|[A-PR-UWYZ][0-9][A-HJKPSTUW]|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y]) ?[0-9][ABD-HJLNP-UW-Z]{2})$/',
            $postcode,
        ) === 1;
    }
}
