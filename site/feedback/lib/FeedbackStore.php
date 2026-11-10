<?php
declare(strict_types=1);

final class FeedbackStore
{
    public function __construct(private string $directory)
    {
        clearstatcache();
        if (!str_starts_with($directory, '/') || realpath($directory) !== $directory
            || !is_dir($directory) || (fileperms($directory) & 0077) !== 0) {
            throw new RuntimeException('Private storage is unavailable.');
        }
    }

    private function regular(string $path): void
    {
        clearstatcache(true, $path);
        if (is_link($path) || !is_file($path) || (fileperms($path) & 0077) !== 0) {
            throw new RuntimeException('Private storage is unavailable.');
        }
    }

    private function load(): array
    {
        $path = $this->directory . '/quotes.json';
        $this->regular($path);
        if (filesize($path) > 1000000) throw new RuntimeException('Invalid storage.');
        $data = json_decode((string) file_get_contents($path), true, 32, JSON_THROW_ON_ERROR);
        if (!is_array($data) || !isset($data['revision'], $data['records'])
            || !is_int($data['revision']) || $data['revision'] < 0 || !is_array($data['records'])) {
            throw new RuntimeException('Invalid storage.');
        }
        self::validate($data['records']);
        return $data;
    }

    public static function validate(array $records): void
    {
        if (!array_is_list($records) || count($records) > 100) throw new InvalidArgumentException('Maximum 100 quotes.');
        $ids = [];
        foreach ($records as $r) {
            if (!is_array($r) || count($r) !== 6 || !is_string($r['id'] ?? null)
                || !preg_match('/\A[a-f0-9]{32}\z/', $r['id']) || isset($ids[$r['id']])
                || !is_int($r['order'] ?? null) || $r['order'] < 0 || $r['order'] > 999
                || !in_array($r['status'] ?? null, ['draft', 'published'], true)
                || !is_bool($r['consent'] ?? null) || ($r['status'] === 'published' && !$r['consent'])) {
                throw new InvalidArgumentException('Invalid quote or missing publication permission.');
            }
            foreach (['text'=>600, 'attribution'=>100] as $key=>$limit) {
                if (!is_string($r[$key] ?? null) || trim($r[$key]) === '' || !mb_check_encoding($r[$key], 'UTF-8')
                    || mb_strlen($r[$key]) > $limit || preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', $r[$key])) {
                    throw new InvalidArgumentException('Check quote and attribution lengths.');
                }
            }
            $ids[$r['id']] = true;
        }
    }

    public function read(): array { return $this->load(); }

    public function save(array $records, int $expectedRevision): int
    {
        self::validate($records);
        clearstatcache();
        if ((fileperms($this->directory) & 0200) === 0) throw new RuntimeException('Storage is not writable.');
        $path = $this->directory . '/quotes.lock';
        if (file_exists($path) || is_link($path)) $this->regular($path);
        $mask = umask(0077);
        try { $lock = fopen($path, 'c'); } finally { umask($mask); }
        if ($lock === false) throw new RuntimeException('Cannot lock storage.');
        $temporary = null;
        try {
            if (!flock($lock, LOCK_EX)) throw new RuntimeException('Cannot lock storage.');
            $current = $this->load();
            if ($current['revision'] !== $expectedRevision) throw new DomainException('Someone changed the quotes. Reload before saving.');
            $revision = $expectedRevision + 1;
            $json = json_encode(['revision'=>$revision, 'records'=>$records], JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
            $temporary = tempnam($this->directory, '.quotes-');
            if ($temporary === false || !chmod($temporary,0600)
                || file_put_contents($temporary,$json) !== strlen($json)
                || !rename($temporary,$this->directory . '/quotes.json')) throw new RuntimeException('Cannot save feedback.');
            $temporary = null;
            return $revision;
        } finally {
            if (is_string($temporary) && is_file($temporary)) unlink($temporary);
            flock($lock, LOCK_UN);
            fclose($lock);
        }
    }

    public function published(): array
    {
        $records = array_values(array_filter($this->read()['records'], fn($r) => $r['status'] === 'published'));
        usort($records, fn($a,$b) => [$a['order'],$a['id']] <=> [$b['order'],$b['id']]);
        return array_map(fn($r) => ['text'=>$r['text'], 'attribution'=>$r['attribution'], 'order'=>$r['order']], $records);
    }
}
