<?php
declare(strict_types=1);
$source = __DIR__.'/../../site/feedback/lib/FeedbackAuth.php';
if (!is_file($source)) { fwrite(STDERR,"FAIL: FeedbackAuth implementation missing\n"); exit(1); }
require $source;
$dir = sys_get_temp_dir().'/feedback-auth-'.bin2hex(random_bytes(8));
mkdir($dir,0700); $dir=realpath($dir); mkdir("$dir/sessions",0700);
$config=['environment'=>'local','username'=>'melanie','directory'=>$dir,'password_hash'=>password_hash('test-only-long-password',PASSWORD_DEFAULT)];
function verify(bool $ok,string $message):void { if (!$ok) throw new RuntimeException($message); }
try {
    $auth=new FeedbackAuth($config);
    verify(!$auth->authenticated(),'Starts logged out');
    $token=$auth->csrfToken();
    verify($auth->verifyCsrf($token) && !$auth->verifyCsrf('wrong'),'CSRF');
    $old=session_id();
    verify(!$auth->login('someone','test-only-long-password'),'Sole user');
    verify($auth->login('melanie','test-only-long-password'),'Valid password');
    verify(session_id()!==$old && !$auth->verifyCsrf($token),'Rotate session and CSRF');
    verify($auth->authenticated(),'Authenticated');
    $_SESSION['feedback']['last']=time()-1801;
    verify(!$auth->authenticated(),'Idle timeout');
    $auth->login('melanie','test-only-long-password');
    $_SESSION['feedback']['created']=time()-28801;
    verify(!$auth->authenticated(),'Absolute timeout');
    $auth->login('melanie','test-only-long-password');
    $auth->logout(); verify(!$auth->authenticated(),'Logout');
    for($i=0;$i<5;$i++) verify(!$auth->login('melanie','wrong'),'Wrong password');
    verify(!$auth->login('melanie','test-only-long-password'),'Throttle valid password after five failures');
    file_put_contents("$dir/login-attempts.json",json_encode(array_fill(0,5,time()-901)));
    verify($auth->login('melanie','test-only-long-password'),'Throttle expiry');
    $_SESSION['feedback']['credential']='obsolete';
    verify(!$auth->authenticated(),'Credential change revokes session');
    session_write_close();
    echo "FeedbackAuth tests passed\n";
} finally {
    foreach(glob("$dir/sessions/*") as $file) unlink($file);
    rmdir("$dir/sessions");
    foreach(glob("$dir/*") as $file) unlink($file);
    rmdir($dir);
}
