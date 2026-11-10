<?php
declare(strict_types=1);
require dirname(__DIR__).'/lib/bootstrap.php';
require dirname(__DIR__).'/lib/FeedbackAuth.php';
feedbackHeaders();
$escape=static fn(string $s):string=>htmlspecialchars($s,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');
$field=static function(string $key,string $default=''):string {
    $value=$_POST[$key] ?? $default;
    if (!is_string($value)) throw new InvalidArgumentException('Invalid form input.');
    return $value;
};
$message='';
$editing=null;
try {
    $config=feedbackConfig();
    $store=new FeedbackStore($config['directory']);
    $auth=new FeedbackAuth($config);
    if (!in_array($_SERVER['REQUEST_METHOD'],['GET','POST'],true)) {
        http_response_code(405); header('Allow: GET, POST'); exit;
    }
    if ($_SERVER['REQUEST_METHOD']==='POST') {
        try {
            if (!$auth->verifyCsrf($field('csrf')) || (isset($_SERVER['HTTP_ORIGIN']) && $_SERVER['HTTP_ORIGIN']!==$config['origin'])) {
                http_response_code(403); $message='This form has expired. Reload and try again.';
            } else {
                $action=$field('action');
                if ($action==='login') {
                    if (!$auth->login($field('username'),$field('password'))) {
                        http_response_code(401); $message='Unable to sign in. Check your details, or wait 15 minutes before trying again.';
                    } else { header('Location: /feedback/admin/',true,303); exit; }
                } else {
                    $auth->requireAuthenticated();
                    if ($action==='logout') { $auth->logout(); header('Location: /feedback/admin/',true,303); exit; }
                    $revision=filter_var($field('revision'),FILTER_VALIDATE_INT,['options'=>['min_range'=>0]]);
                    if ($revision===false) throw new InvalidArgumentException('Invalid revision. Reload the page.');
                    $data=$store->read(); $records=$data['records'];
                    if ($data['revision']!==$revision) throw new DomainException('Someone changed the quotes. Reload before saving.');
                    $id=$field('id'); $index=null;
                    foreach($records as $i=>$record) if ($record['id']===$id) $index=$i;
                    if ($id!=='' && $index===null) throw new InvalidArgumentException('Quote not found.');
                    if ($action==='save') {
                        $order=filter_var($field('order'),FILTER_VALIDATE_INT,['options'=>['min_range'=>0,'max_range'=>999]]);
                        if ($order===false) throw new InvalidArgumentException('Order must be between 0 and 999.');
                        $record=['id'=>$id ?: bin2hex(random_bytes(16)),'text'=>trim($field('text')),'attribution'=>trim($field('attribution')),'order'=>$order,'status'=>'draft','consent'=>false];
                        if ($index===null) $records[]=$record; else $records[$index]=$record;
                    } elseif ($index!==null && $action==='publish') {
                        if ($field('permission')!=='yes') throw new InvalidArgumentException('Confirm permission to publish this exact quote and attribution.');
                        $records[$index]['consent']=true; $records[$index]['status']='published';
                    } elseif ($index!==null && $action==='unpublish') {
                        $records[$index]['status']='draft';
                    } elseif ($index!==null && $action==='delete') {
                        if ($field('confirm')!=='yes') throw new InvalidArgumentException('Confirm deletion first.');
                        array_splice($records,$index,1);
                    } else throw new InvalidArgumentException('Choose a valid action.');
                    $store->save($records,$revision);
                    $_SESSION['feedback_notice']='Your change has been saved.';
                    header('Location: /feedback/admin/',true,303); exit;
                }
            }
        } catch (DomainException $e) { http_response_code(409); $message=$e->getMessage(); }
        catch (InvalidArgumentException $e) { http_response_code(422); $message=$e->getMessage(); }
        catch (UnexpectedValueException $e) { http_response_code(401); $message='Please sign in again.'; }
    }
    $signedIn=$auth->authenticated();
    $csrf=$auth->csrfToken();
    if ($signedIn) {
        $data=$store->read();
        $edit=$_GET['edit'] ?? '';
        foreach($data['records'] as $r) if (is_string($edit) && $r['id']===$edit) $editing=$r;
        usort($data['records'],fn($a,$b)=>[$a['order'],$a['id']]<=>[$b['order'],$b['id']]);
    }
    if ($message==='') $message=is_string($_SESSION['feedback_notice'] ?? null) ? $_SESSION['feedback_notice'] : '';
    unset($_SESSION['feedback_notice']);
} catch (Throwable $e) {
    http_response_code(503);
    echo 'Feedback management is temporarily unavailable. Please contact your website administrator.';
    exit;
}
?>
<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Feedback manager | Stronger at Home</title>
  <link rel="stylesheet" href="/assets/css/brand-tokens.css">
  <link rel="stylesheet" href="/assets/css/feedback-admin.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header><a href="/">Stronger at Home</a><span>Private feedback manager</span></header>
<main id="main">
<?php if ($config['environment']==='local'): ?><p class="notice">Local preview only — sample content, not patient feedback. No live website is connected.</p><?php endif; ?>
<?php if ($message!==''): ?><p class="notice" role="status"><?= $escape($message) ?></p><?php endif; ?>
<?php if (!$signedIn): ?>
  <section class="login"><p class="eyebrow">Melanie’s workspace</p><h1>Sign in</h1>
  <p>Manage the quotes displayed on your website.</p>
  <form method="post" action="/feedback/admin/">
    <input type="hidden" name="csrf" value="<?= $escape($csrf) ?>">
    <input type="hidden" name="action" value="login">
    <label for="username">Username</label><input id="username" name="username" value="melanie" autocomplete="username" required maxlength="100">
    <label for="password">Password</label><input id="password" type="password" name="password" autocomplete="current-password" required maxlength="1024">
    <button type="submit">Sign in</button>
  </form><p class="hint">Forgotten your password? Ask your website administrator to reset it privately.</p></section>
<?php else: ?>
  <div class="heading"><div><p class="eyebrow">Melanie’s workspace</p><h1>Manage feedback</h1></div>
  <form method="post" action="/feedback/admin/"><input type="hidden" name="csrf" value="<?= $escape($csrf) ?>"><button class="secondary" name="action" value="logout">Sign out</button></form></div>
  <p>Save a draft, review the quote, then publish when you have permission. Changes appear on the website when the page is refreshed.</p>
  <p class="hint">Use only the words and attribution agreed for public display. Do not enter original messages or private medical details. Saving an edit returns a published quote to draft.</p>
  <div class="workspace">
  <section class="editor" aria-labelledby="editor-heading">
    <h2 id="editor-heading"><?= $editing ? 'Edit quote' : 'Add a quote' ?></h2>
    <form method="post" action="/feedback/admin/">
      <input type="hidden" name="csrf" value="<?= $escape($csrf) ?>"><input type="hidden" name="action" value="save">
      <input type="hidden" name="revision" value="<?= $data['revision'] ?>"><input type="hidden" name="id" value="<?= $escape($editing['id'] ?? '') ?>">
      <label for="quote">Quote <span>(up to 600 characters)</span></label>
      <textarea id="quote" name="text" required maxlength="600" rows="6"><?= $escape($editing['text'] ?? '') ?></textarea>
      <label for="attribution">Public attribution <span>(up to 100 characters)</span></label>
      <input id="attribution" name="attribution" required maxlength="100" value="<?= $escape($editing['attribution'] ?? '') ?>" aria-describedby="attribution-help">
      <p class="hint" id="attribution-help">For example, an agreed first name or “Patient’s family member”.</p>
      <label for="order">Display order <span>(lower numbers appear first)</span></label>
      <input id="order" type="number" name="order" min="0" max="999" required value="<?= $editing['order'] ?? 10 ?>">
      <button>Save draft</button> <a href="/feedback/admin/">Clear editor</a>
    </form>
  </section>
  <section aria-labelledby="quotes-heading"><h2 id="quotes-heading">Your quotes <span>(<?= count($data['records']) ?>)</span></h2>
  <?php if (!$data['records']): ?><p>No quotes yet. Add your first approved excerpt as a draft.</p><?php endif; ?>
  <?php foreach($data['records'] as $r): ?>
    <article class="quote-card">
      <p class="badge"><?= $r['status']==='published' ? 'Published' : 'Draft — not public' ?> · Order <?= $r['order'] ?></p>
      <h3>Quote preview</h3><blockquote><p><?= nl2br($escape($r['text'])) ?></p><footer><?= $escape($r['attribution']) ?></footer></blockquote>
      <a href="/feedback/admin/?edit=<?= $r['id'] ?>">Edit quote</a>
      <form method="post" action="/feedback/admin/">
        <input type="hidden" name="csrf" value="<?= $escape($csrf) ?>"><input type="hidden" name="revision" value="<?= $data['revision'] ?>"><input type="hidden" name="id" value="<?= $r['id'] ?>">
        <?php if($r['status']==='draft'): ?>
        <label class="check"><input type="checkbox" name="permission" value="yes" required> I have permission to publish this exact quote and attribution.</label>
        <button name="action" value="publish">Publish quote</button>
        <?php else: ?><button class="secondary" name="action" value="unpublish">Unpublish quote</button><?php endif; ?>
      </form>
      <details><summary>Delete quote</summary><form method="post" action="/feedback/admin/">
        <input type="hidden" name="csrf" value="<?= $escape($csrf) ?>"><input type="hidden" name="revision" value="<?= $data['revision'] ?>"><input type="hidden" name="id" value="<?= $r['id'] ?>">
        <label class="check"><input type="checkbox" name="confirm" value="yes" required> Delete this quote permanently.</label><button class="secondary" name="action" value="delete">Confirm deletion</button>
      </form></details>
    </article>
  <?php endforeach; ?></section></div>
<?php endif; ?>
</main></body></html>
