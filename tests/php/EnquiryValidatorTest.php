<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

use StrongerAtHome\Enquiry\EnquiryValidator;

$valid = [
    'name' => 'Alex Morgan',
    'email' => 'alex@example.com',
    'phone' => '',
    'preferred_contact' => 'email',
    'postcode' => 'KT17 4LZ',
    'message' => 'I would like to discuss a home assessment.',
    'privacy_acknowledged' => '1',
    'website' => '',
];
$result = (new EnquiryValidator())->validate($valid);
assert_true($result->isValid(), 'valid enquiry is accepted');
assert_same('KT17 4LZ', $result->data['postcode'], 'postcode is normalised');

$missingEmail = $valid;
$missingEmail['email'] = '';
$result = (new EnquiryValidator())->validate($missingEmail);
assert_same('Please provide an email address.', $result->errors['email'], 'preferred email is required');

$tooLong = $valid;
$tooLong['message'] = str_repeat('x', 1001);
assert_true(isset((new EnquiryValidator())->validate($tooLong)->errors['message']), 'message is bounded');

$tooLongEmail = $valid;
$tooLongEmail['email'] = str_repeat('a', 244) . '@example.com';
assert_true(isset((new EnquiryValidator())->validate($tooLongEmail)->errors['email']), 'email is bounded');

$headerInjection = $valid;
$headerInjection['name'] = "Alex\r\nBcc: attacker@example.com";
assert_true(isset((new EnquiryValidator())->validate($headerInjection)->errors['name']), 'header controls are rejected');

$honeypot = $valid;
$honeypot['website'] = 'bot.example';
assert_true(isset((new EnquiryValidator())->validate($honeypot)->errors['website']), 'honeypot submissions are rejected');

$invalidEncoding = $valid;
$invalidEncoding['message'] = "Invalid \xC3";
assert_true(isset((new EnquiryValidator())->validate($invalidEncoding)->errors['message']), 'invalid UTF-8 is rejected');

$arrayInput = $valid;
$arrayInput['name'] = ['Alex'];
assert_true(isset((new EnquiryValidator())->validate($arrayInput)->errors['name']), 'non-scalar field input is rejected');
