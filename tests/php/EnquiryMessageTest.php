<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

use StrongerAtHome\Enquiry\EnquiryMessage;

$message = EnquiryMessage::from([
    'name' => 'Alex <script>alert(1)</script>',
    'email' => 'alex@example.com',
    'phone' => '07123 456789',
    'preferred_contact' => 'email',
    'postcode' => 'KT17 4LZ',
    'message' => "Please call me.\nThank you.",
    'website' => 'not included',
    'csrf_token' => 'not included',
]);
assert_same('New website appointment request', $message->subject, 'subject has no personal data');
assert_true(!str_contains($message->htmlBody, '<script>'), 'HTML escapes input');
assert_true(str_contains($message->textBody, 'KT17 4LZ'), 'text body includes postcode');
assert_same('alex@example.com', $message->replyToEmail, 'valid email is reply-to');
assert_true(!str_contains($message->textBody, 'not included'), 'message excludes non-enquiry fields');
assert_true(!str_contains($message->htmlBody, 'not included'), 'HTML excludes non-enquiry fields');
