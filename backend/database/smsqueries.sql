SELECT fileID, domain, relativePath 
FROM Files 
WHERE relativePath LIKE '%sms.db%';

SELECT
    ROWID       AS handle_id,
    id          AS phone_number,
    service     AS message_service
FROM handle
ORDER BY ROWID ASC;


SELECT 
  ROWID, 
  text, 
  date, 
  is_from_me 
FROM message 
WHERE handle_id = 16 
ORDER BY date ASC;