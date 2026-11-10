<?php
declare(strict_types=1);
// Operator-only: pipe a password from protected input, never pass it as an argument.
if (PHP_SAPI!=='cli') { http_response_code(404); exit; }
try {
    $options=getopt('',['directory:','environment:','origin:','password-stdin','rotate']);
    $directory=$options['directory'] ?? '';
    $environment=$options['environment'] ?? '';
    $origin=$options['origin'] ?? '';
    if (!isset($options['password-stdin']) || !is_string($directory) || !str_starts_with($directory,'/')
        || !in_array($environment,['local','staging','production'],true)) throw new RuntimeException('Specify private directory, environment, origin and --password-stdin.');
    $parent=realpath(dirname($directory));
    $public=realpath(__DIR__.'/../site');
    if (!$parent || $parent.'/'.basename($directory)!==$directory || $directory===$public
        || str_starts_with($directory,$public.'/') || str_contains($directory,'/public_html/')) throw new RuntimeException('Use a canonical private path outside web roots.');
    if ($environment==='local') {
        if (!preg_match('~^http://127[.]0[.]0[.]1:[0-9]{2,5}$~D',$origin)) throw new RuntimeException('Local origin must be loopback.');
    } elseif ($origin!==($environment==='staging' ? 'https://staging.stronger-at-home.co.uk' : 'https://stronger-at-home.co.uk')) {
        throw new RuntimeException('Unexpected origin.');
    }
    $password=rtrim((string)stream_get_contents(STDIN,1025),"\r\n");
    if (strlen($password)<16 || strlen($password)>72) throw new RuntimeException('Use a unique password of 16–72 bytes.');
    $mask=umask(0077);
    if (!file_exists($directory) && !mkdir($directory,0700)) throw new RuntimeException('Cannot create private directory.');
    if (is_link($directory) || realpath($directory)!==$directory || (fileperms($directory)&0077)!==0) throw new RuntimeException('Directory must be private (0700), not a symlink.');
    $path=$directory.'/feedback.php';
    $exists=file_exists($path);
    if (is_link($path) || ($exists && !isset($options['rotate']))) throw new RuntimeException('Already configured. Use --rotate to change password only.');
    if ($exists) {
        $current=require $path;
        if (($current['environment'] ?? null)!==$environment || ($current['origin'] ?? null)!==$origin
            || ($current['directory'] ?? null)!==$directory) throw new RuntimeException('Rotation must preserve environment, origin and directory.');
    }
    if (!$exists && (file_exists($directory.'/quotes.json') || is_link($directory.'/quotes.json'))) throw new RuntimeException('Existing data requires manual review.');
    $sessions=$directory.'/sessions';
    if (!file_exists($sessions) && !mkdir($sessions,0700)) throw new RuntimeException('Cannot create private sessions.');
    if (is_link($sessions) || !is_dir($sessions) || (fileperms($sessions)&0077)!==0) throw new RuntimeException('Unsafe sessions directory.');
    if (!$exists && file_put_contents($directory.'/quotes.json','{"revision":0,"records":[]}')===false) throw new RuntimeException('Cannot initialise storage.');
    $config=['environment'=>$environment,'origin'=>$origin,'username'=>'melanie','password_hash'=>password_hash($password,PASSWORD_DEFAULT),'directory'=>$directory];
    unset($password);
    $temporary=tempnam($directory,'.config-');
    if ($temporary===false || !chmod($temporary,0600)
        || file_put_contents($temporary,"<?php\nreturn ".var_export($config,true).";\n")===false
        || !rename($temporary,$path)) throw new RuntimeException('Cannot save private configuration.');
    umask($mask);
    echo "Private feedback configuration ready. No website has been deployed.\n";
} catch(Throwable $e) {
    fwrite(STDERR,$e->getMessage()."\n"); exit(1);
}
