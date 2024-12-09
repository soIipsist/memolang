var user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/605.1.15'
navigator.__defineGetter__('userAgent', function() { return user_agent; });
