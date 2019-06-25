detect_related_urls
=====

## Input

SNS Message Event

```
{
    "Records": [
        "Sns": {
            "Message": "$message"
        }
    ]
}
```

$message

```
{
    "urls": ["http://example.com/article01","http://example.com/article02",...],
    "username": "",
    "message": "string",
    "target_topic_arns": ["arn1","arn2"]
}
```
