<?php
declare(strict_types=1);
http_response_code(503);
header('Content-Type: text/plain; charset=UTF-8');
header('Cache-Control: no-store');
echo "Online appointment requests are temporarily unavailable.\n";
exit;
