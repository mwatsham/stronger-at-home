<?php
declare(strict_types=1);
$source = __DIR__ . '/../../site/feedback/lib/FeedbackStore.php';
if (!is_file($source)) { fwrite(STDERR, "FAIL: FeedbackStore implementation missing\n"); exit(1); }
require $source;
function check(bool $ok, string $label): void { if (!$ok) throw new RuntimeException($label); }
function rejects(callable $f, string $label): void {
    try { $f(); } catch (Throwable $e) { return; }
    throw new RuntimeException($label);
}
$dir = sys_get_temp_dir() . '/feedback-test-' . bin2hex(random_bytes(8));
mkdir($dir, 0700);
$dir = realpath($dir);
try {
    rejects(fn() => (new FeedbackStore($dir))->read(), 'Missing store must fail');
    file_put_contents("$dir/quotes.json", '{"revision":0,"records":[]}');
    chmod("$dir/quotes.json", 0600);
    $store = new FeedbackStore($dir);
    check($store->read()['revision'] === 0, 'Initial revision');
    $quote = ['id'=>bin2hex(random_bytes(16)), 'text'=>'Helpful support', 'attribution'=>'Patient', 'order'=>1, 'status'=>'draft', 'consent'=>false];
    check($store->save([$quote], 0) === 1, 'Save draft');
    check($store->published() === [], 'Draft must be private');
    rejects(fn() => $store->save([], 0), 'Stale edit must fail');
    $quote['status'] = 'published';
    rejects(fn() => $store->save([$quote], 1), 'Publish requires permission');
    $quote['consent'] = true;
    $store->save([$quote], 1);
    check($store->published() === [['text'=>'Helpful support','attribution'=>'Patient','order'=>1]], 'Public projection');
    foreach (['text'=>'', 'attribution'=>str_repeat('x',101), 'order'=>-1, 'status'=>'invalid', 'consent'=>'yes'] as $key=>$value) {
        $bad=$quote; $bad[$key]=$value;
        rejects(fn() => $store->save([$bad],2), "Reject $key");
    }
    $bad=$quote; $bad['text']=str_repeat('x',601);
    rejects(fn() => $store->save([$bad],2), 'Quote bound');
    rejects(fn() => $store->save([$quote,$quote],2), 'Duplicate IDs');
    chmod($dir, 0500);
    rejects(fn() => $store->save([],2), 'Unwritable store');
    chmod($dir, 0700);
    check($store->read()['revision'] === 2, 'Failed writes preserve data');
    $store->save([],2);
    check($store->published() === [], 'Delete persists');
    file_put_contents("$dir/quotes.json", 'broken');
    rejects(fn() => $store->read(), 'Corrupt data fails closed');
    unlink("$dir/quotes.json");
    symlink(__FILE__, "$dir/quotes.json");
    rejects(fn() => $store->read(), 'Symlink rejected');
    echo "FeedbackStore tests passed\n";
} finally {
    chmod($dir,0700);
    foreach (glob("$dir/*") as $file) unlink($file);
    rmdir($dir);
}
