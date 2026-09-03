<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

use InvalidArgumentException;

final class FileRateLimiter implements RateLimit
{
    public function __construct(
        private string $directory,
        private string $secret,
        private int $maximum,
        private int $windowSeconds,
    ) {
        if ($directory === '' || $secret === '' || $maximum < 1 || $windowSeconds < 1) {
            throw new InvalidArgumentException('Rate-limit configuration is invalid.');
        }
    }

    public function allow(string $clientAddress, int $now): bool
    {
        if (!$this->ensurePrivateDirectory()) {
            return false;
        }

        $key = hash_hmac('sha256', $clientAddress, $this->secret);
        $path = $this->directory . DIRECTORY_SEPARATOR . $key . '.json';
        $created = false;
        $previousUmask = umask(0077);
        try {
            $handle = @fopen($path, 'x+');
            if ($handle !== false) {
                $created = true;
            } else {
                $handle = @fopen($path, 'r+');
            }
        } finally {
            umask($previousUmask);
        }

        if ($handle === false) {
            return false;
        }

        $allowed = false;
        try {
            if (!flock($handle, LOCK_EX)) {
                return false;
            }

            if (!@chmod($path, 0600)) {
                return false;
            }
            if ($created) {
                $state = ['window_started' => $now, 'count' => 0];
            } else {
                rewind($handle);
                $raw = stream_get_contents($handle);
                if (!is_string($raw) || $raw === '') {
                    return false;
                }
                try {
                    $state = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
                } catch (\JsonException) {
                    return false;
                }
                if (!$this->isValidState($state, $now)) {
                    return false;
                }

                $state = [
                    'window_started' => $state['window_started'],
                    'count' => $state['count'],
                ];
                if ($now - $state['window_started'] >= $this->windowSeconds) {
                    $state = ['window_started' => $now, 'count' => 0];
                }
            }

            if ($state['count'] >= $this->maximum) {
                return false;
            }

            $state['count']++;
            $encoded = json_encode($state);
            if (!is_string($encoded)) {
                return false;
            }

            rewind($handle);
            if (!ftruncate($handle, 0)) {
                return false;
            }
            if (fwrite($handle, $encoded) !== strlen($encoded) || !fflush($handle)) {
                return false;
            }

            $allowed = true;
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }

        if ($allowed) {
            try {
                if (random_int(1, 100) === 1) {
                    $this->cleanup($now);
                }
            } catch (\Throwable) {
                // Cleanup is opportunistic and must not change an accepted request.
            }
        }

        return $allowed;
    }

    private function ensurePrivateDirectory(): bool
    {
        if (is_link($this->directory)) {
            return false;
        }

        $previousUmask = umask(0077);
        try {
            if (!is_dir($this->directory) && !@mkdir($this->directory, 0700, true) && !is_dir($this->directory)) {
                return false;
            }
        } finally {
            umask($previousUmask);
        }

        return @chmod($this->directory, 0700);
    }

    /**
     * @param mixed $state
     */
    private function isValidState($state, int $now): bool
    {
        if (!is_array($state)
            || !isset($state['window_started'], $state['count'])
            || !is_int($state['window_started'])
            || !is_int($state['count'])
            || $state['window_started'] > $now
            || $state['count'] < 0
        ) {
            return false;
        }

        return true;
    }

    private function cleanup(int $now): void
    {
        try {
            $entries = new \FilesystemIterator($this->directory, \FilesystemIterator::SKIP_DOTS);
        } catch (\UnexpectedValueException) {
            return;
        }

        $scanned = 0;
        foreach ($entries as $entry) {
            if ($scanned++ >= 20) {
                break;
            }
            if (!$entry->isFile() || $entry->isLink() || preg_match('/\A[a-f0-9]{64}\.json\z/', $entry->getFilename()) !== 1) {
                continue;
            }

            $handle = @fopen($entry->getPathname(), 'r');
            if ($handle === false) {
                continue;
            }
            try {
                if (!flock($handle, LOCK_EX | LOCK_NB)) {
                    continue;
                }
                $metadata = fstat($handle);
                if (is_array($metadata) && isset($metadata['mtime']) && (int) $metadata['mtime'] <= $now - (2 * $this->windowSeconds)) {
                    @unlink($entry->getPathname());
                }
            } finally {
                flock($handle, LOCK_UN);
                fclose($handle);
            }
        }
    }
}
