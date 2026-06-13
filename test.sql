INSERT OR IGNORE INTO users (user_id) VALUES (123456789);

INSERT OR IGNORE INTO mood (user_id, entry_date, mood, hours_work, hours_sleep, comment) VALUES
(6318736411, date('now', '-14 days'), 4, 5.0, 8.0, 'Хороший день'),
(6318736411, date('now', '-13 days'), 3, 3.0, 6.5, NULL),
(6318736411, date('now', '-12 days'), 2, 7.0, 5.0, 'Устал'),
(6318736411, date('now', '-11 days'), 5, 4.0, 9.0, 'Отличный день'),
(6318736411, date('now', '-10 days'), 4, 6.0, 8.0, NULL),
(6318736411, date('now', '-9 days'),  3, 2.0, 7.0, NULL),
(6318736411, date('now', '-8 days'),  1, 8.0, 4.5, 'Очень устал'),
(6318736411, date('now', '-7 days'),  4, 4.0, 8.5, NULL),
(6318736411, date('now', '-6 days'),  5, 5.0, 9.0, 'Выспался'),
(6318736411, date('now', '-5 days'),  3, 6.0, 6.0, NULL),
(6318736411, date('now', '-4 days'),  2, 7.5, 5.5, 'Много работы'),
(6318736411, date('now', '-3 days'),  4, 3.0, 8.0, NULL),
(6318736411, date('now', '-2 days'),  5, 4.5, 8.5, 'Продуктивно'),
(6318736411, date('now', '-1 days'),  3, 5.0, 7.0, NULL),
(6318736411, date('now'),             4, 4.0, 8.0, 'Сегодня норм');
