<?php
declare(strict_types=1);

final class FeedbackAuth
{
    public function __construct(private array $config)
    {
        $sessions=$config['directory'].'/sessions';
        if (is_link($sessions) || !is_dir($sessions) || realpath($sessions)!==$sessions
            || (fileperms($sessions)&0077)!==0) throw new RuntimeException('Private sessions unavailable.');
        ini_set('session.use_strict_mode','1');
        ini_set('session.use_only_cookies','1');
        session_name('SAHFeedback');
        session_save_path($sessions);
        session_set_cookie_params(['lifetime'=>0,'path'=>'/feedback/admin/','secure'=>$config['environment']!=='local','httponly'=>true,'samesite'=>'Strict']);
        if (!session_start()) throw new RuntimeException('Cannot start secure session.');
    }

    public function csrfToken(): string
    {
        if (!is_string($_SESSION['feedback_csrf'] ?? null)) $_SESSION['feedback_csrf']=bin2hex(random_bytes(32));
        return $_SESSION['feedback_csrf'];
    }

    public function verifyCsrf(string $token): bool { return hash_equals($this->csrfToken(),$token); }

    public function authenticated(): bool
    {
        $state=$_SESSION['feedback'] ?? [];
        if (!is_array($state) || ($state['user'] ?? '')!=='melanie'
            || !is_int($state['last'] ?? null) || !is_int($state['created'] ?? null)
            || time()-$state['last']>1800 || time()-$state['created']>28800
            || ($state['credential'] ?? '')!==hash('sha256',$this->config['password_hash'])) {
            unset($_SESSION['feedback']);
            return false;
        }
        $_SESSION['feedback']['last']=time();
        return true;
    }

    public function requireAuthenticated(): void
    {
        if (!$this->authenticated()) throw new UnexpectedValueException('Please sign in.');
    }

    public function login(string $username,string $password): bool
    {
        $file=$this->config['directory'].'/login-attempts.json';
        clearstatcache(true,$file);
        if (is_link($file) || (file_exists($file) && (!is_file($file) || (fileperms($file)&0077)!==0))) {
            throw new RuntimeException('Login protection unavailable.');
        }
        $mask=umask(0077);
        try { $handle=fopen($file,'c+'); } finally { umask($mask); }
        if (!$handle) throw new RuntimeException('Login protection unavailable.');
        try {
            if (!flock($handle,LOCK_EX)) throw new RuntimeException('Login protection unavailable.');
            $raw=stream_get_contents($handle,4097);
            if ($raw===false || strlen($raw)>4096) throw new RuntimeException('Login protection unavailable.');
            $attempts=$raw==='' ? [] : json_decode($raw,true,8,JSON_THROW_ON_ERROR);
            if (!is_array($attempts) || !array_is_list($attempts) || count($attempts)>5) throw new RuntimeException('Invalid login protection.');
            foreach($attempts as $stamp) if (!is_int($stamp)) throw new RuntimeException('Invalid login protection.');
            $attempts=array_values(array_filter($attempts,fn($stamp)=>$stamp>time()-900));
            if (count($attempts)>=5) return false;
            $valid=strlen($password)<=1024 && password_verify($password,$this->config['password_hash']) && $username==='melanie';
            $attempts=$valid ? [] : [...$attempts,time()];
            $json=json_encode($attempts,JSON_THROW_ON_ERROR);
            rewind($handle);
            if (!ftruncate($handle,0) || fwrite($handle,$json)!==strlen($json) || !fflush($handle)) throw new RuntimeException('Cannot record login attempt.');
        } finally { flock($handle,LOCK_UN); fclose($handle); }
        if (!$valid) return false;
        if (!session_regenerate_id(true)) throw new RuntimeException('Cannot secure session.');
        $_SESSION=['feedback'=>['user'=>'melanie','created'=>time(),'last'=>time(),'credential'=>hash('sha256',$this->config['password_hash'])]];
        return true;
    }

    public function logout(): void
    {
        $_SESSION=[];
        if (!session_regenerate_id(true)) throw new RuntimeException('Cannot close session.');
    }
}
