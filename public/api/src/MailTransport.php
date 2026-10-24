<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

interface MailTransport
{
    public function send(EnquiryMessage $message): void;
}
