<?php
declare(strict_types=1);
require __DIR__ . '/lib/bootstrap.php';
feedbackHeaders();
header('Content-Type: application/json; charset=utf-8');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'GET') {
    http_response_code(405); header('Allow: GET'); echo '{"quotes":[]}'; exit;
}
try {
    $config = feedbackConfig();
    echo json_encode(['quotes'=>(new FeedbackStore($config['directory']))->published()], JSON_THROW_ON_ERROR);
} catch (Throwable $error) {
    http_response_code(503);
    echo '{"quotes":[]}';
}
