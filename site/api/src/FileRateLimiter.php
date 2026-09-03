<?php
declare(strict_types=1);

namespace StrongerAtHome\Enquiry;

use InvalidArgumentException;

final class FileRateLimiter implements RateLimit
{
    private const CLEANUP_BATCH_SIZE = 20;
    private const MAXIMUM_COUNTER_FILES = 4096;
    private const MAINTENANCE_FILENAME = '.rate-limit-maintenance';

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

        $maintenance = $this->openMaintenanceFile();
        if ($maintenance === false) {
            return false;
        }

        try {
            if (!flock($maintenance, LOCK_EX)) {
                return false;
            }
            if (!$this->cleanup($maintenance, $now)) {
                return false;
            }

            $key = hash_hmac('sha256', $clientAddress, $this->secret);
            $path = $this->directory . DIRECTORY_SEPARATOR . $key . '.json';
            $counterPaths = $this->counterPaths();
            if ($counterPaths === null
                || count($counterPaths) > self::MAXIMUM_COUNTER_FILES
                || (count($counterPaths) === self::MAXIMUM_COUNTER_FILES && !is_file($path))
            ) {
                return false;
            }

            return $this->updateCounter($path, $now);
        } finally {
            flock($maintenance, LOCK_UN);
            fclose($maintenance);
        }
    }

    private function updateCounter(string $path, int $now): bool
    {
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

        try {
            if (!flock($handle, LOCK_EX) || !@chmod($path, 0600)) {
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
            if (!ftruncate($handle, 0)
                || fwrite($handle, $encoded) !== strlen($encoded)
                || !fflush($handle)
            ) {
                return false;
            }

            return true;
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }
    }

    /** @return resource|false */
    private function openMaintenanceFile()
    {
        $path = $this->directory . DIRECTORY_SEPARATOR . self::MAINTENANCE_FILENAME;
        if (is_link($path)) {
            return false;
        }

        $previousUmask = umask(0077);
        try {
            $handle = @fopen($path, 'x+');
            if ($handle === false) {
                $handle = @fopen($path, 'r+');
            }
        } finally {
            umask($previousUmask);
        }

        if ($handle === false || !@chmod($path, 0600)) {
            if (is_resource($handle)) {
                fclose($handle);
            }
            return false;
        }

        return $handle;
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

    /** @param mixed $state */
    private function isValidState($state, int $now): bool
    {
        return is_array($state)
            && isset($state['window_started'], $state['count'])
            && is_int($state['window_started'])
            && is_int($state['count'])
            && $state['window_started'] <= $now
            && $state['count'] >= 0;
    }

    /** @return list<string>|null */
    private function counterPaths(): ?array
    {
        try {
            $entries = new \FilesystemIterator($this->directory, \FilesystemIterator::SKIP_DOTS);
        } catch (\UnexpectedValueException) {
            return null;
        }

        $paths = [];
        foreach ($entries as $entry) {
            if ($entry->isFile()
                && !$entry->isLink()
                && preg_match('/\A[a-f0-9]{64}\.json\z/D', $entry->getFilename()) === 1
            ) {
                $paths[] = $entry->getPathname();
            }
        }
        sort($paths, SORT_STRING);

        return $paths;
    }

    /** @param resource $maintenance */
    private function cleanup($maintenance, int $now): bool
    {
        $paths = $this->counterPaths();
        if ($paths === null) {
            return false;
        }

        rewind($maintenance);
        $cursor = stream_get_contents($maintenance);
        if (!is_string($cursor)
            || ($cursor !== '' && preg_match('/\A[a-f0-9]{64}\.json\z/D', $cursor) !== 1)
        ) {
            return false;
        }

        $start = 0;
        foreach ($paths as $index => $path) {
            if (basename($path) > $cursor) {
                $start = $index;
                break;
            }
        }

        $processed = min(self::CLEANUP_BATCH_SIZE, count($paths));
        $nextCursor = '';
        for ($offset = 0; $offset < $processed; $offset++) {
            $path = $paths[($start + $offset) % count($paths)];
            $nextCursor = basename($path);
            $handle = @fopen($path, 'r+');
            if ($handle === false) {
                continue;
            }
            try {
                if (!flock($handle, LOCK_EX | LOCK_NB)) {
                    continue;
                }
                $metadata = fstat($handle);
                if (is_array($metadata)
                    && isset($metadata['mtime'])
                    && (int) $metadata['mtime'] <= $now - (2 * $this->windowSeconds)
                ) {
                    @unlink($path);
                }
            } finally {
                flock($handle, LOCK_UN);
                fclose($handle);
            }
        }

        rewind($maintenance);
        return ftruncate($maintenance, 0)
            && fwrite($maintenance, $nextCursor) === strlen($nextCursor)
            && fflush($maintenance);
    }
}
