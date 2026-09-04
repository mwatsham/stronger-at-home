<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

use Closure;
use InvalidArgumentException;
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use RuntimeException;

final class PhpMailerTransport implements MailTransport
{
    /**
     * @param array<string, mixed> $config
     * @param null|Closure(): PHPMailer $mailerFactory
     */
    public function __construct(
        private array $config,
        private ?Closure $mailerFactory = null,
    ) {
        $this->assertValidConfiguration();
    }

    public function send(EnquiryMessage $message): void
    {
        try {
            $mailer = $this->mailerFactory === null
                ? new PHPMailer(true)
                : ($this->mailerFactory)();
            if (!$mailer instanceof PHPMailer) {
                throw new RuntimeException('Invalid mailer factory.');
            }

            $mailer->isSMTP();
            $mailer->Host = $this->config['smtp_host'];
            $mailer->SMTPAuth = true;
            $mailer->Username = $this->config['smtp_username'];
            $mailer->Password = $this->config['smtp_password'];
            $mailer->SMTPSecure = $this->config['smtp_encryption'];
            $mailer->Port = $this->config['smtp_port'];
            $mailer->CharSet = 'UTF-8';
            $mailer->SMTPDebug = SMTP::DEBUG_OFF;
            $mailer->setFrom($this->config['sender'], 'Stronger at Home Physiotherapy');
            $mailer->addAddress($this->config['recipient']);
            if ($message->replyToEmail !== '') {
                $mailer->addReplyTo($message->replyToEmail, $message->replyToName);
            }
            $mailer->Subject = $message->subject;
            $mailer->Body = $message->htmlBody;
            $mailer->AltBody = $message->textBody;
            $mailer->isHTML(true);
            $mailer->send();
        } catch (\Throwable) {
            throw new RuntimeException('Unable to deliver enquiry.');
        }
    }

    private function assertValidConfiguration(): void
    {
        foreach (['smtp_host', 'smtp_username', 'smtp_password', 'sender', 'recipient'] as $key) {
            if (!isset($this->config[$key]) || !is_string($this->config[$key]) || trim($this->config[$key]) === '') {
                throw new InvalidArgumentException('Mail configuration is incomplete.');
            }
        }

        if (!isset($this->config['smtp_port'])
            || !is_int($this->config['smtp_port'])
            || $this->config['smtp_port'] < 1
            || $this->config['smtp_port'] > 65535
        ) {
            throw new InvalidArgumentException('Mail configuration has an invalid port.');
        }

        if (!isset($this->config['smtp_encryption'])
            || !is_string($this->config['smtp_encryption'])
            || !in_array($this->config['smtp_encryption'], [PHPMailer::ENCRYPTION_STARTTLS, PHPMailer::ENCRYPTION_SMTPS], true)
        ) {
            throw new InvalidArgumentException('Mail configuration has invalid encryption.');
        }

        if (filter_var($this->config['sender'], FILTER_VALIDATE_EMAIL) === false
            || !str_ends_with(strtolower($this->config['sender']), '@stronger-at-home.co.uk')
        ) {
            throw new InvalidArgumentException('Mail sender must use the Stronger at Home domain.');
        }

        if (filter_var($this->config['recipient'], FILTER_VALIDATE_EMAIL) === false) {
            throw new InvalidArgumentException('Mail recipient is invalid.');
        }
    }
}
