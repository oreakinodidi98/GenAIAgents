param(
    [Parameter(Mandatory)]
    [string] $Image
)

$ErrorActionPreference = 'Stop'
$password = [Guid]::NewGuid().ToString('N')
$startup = (Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\redis-start.sh') -Raw).Trim()
$name = "aca-redis-smoke-$([Guid]::NewGuid().ToString('N'))"
$containerId = & docker run --detach --name $name --network none --env "REDIS_PASSWORD=$password" $Image sh -c $startup
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to start the isolated Redis smoke-test container.'
}

function Invoke-Redis {
    param([string[]] $Arguments)
    $response = & docker exec --env "REDISCLI_AUTH=$password" $containerId redis-cli --raw -e @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Redis command failed: $response"
    }
    return $response
}

try {
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        $pong = & docker exec --env "REDISCLI_AUTH=$password" $containerId redis-cli --raw PING 2>$null
        if ($LASTEXITCODE -eq 0 -and $pong -eq 'PONG') {
            $ready = $true
            break
        }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) {
        & docker logs $containerId
        throw 'Redis did not become ready within 30 seconds.'
    }

    $unauthorized = & docker exec $containerId redis-cli --raw PING
    if ($unauthorized -notmatch 'NOAUTH') {
        throw 'Redis failed to reject an unauthenticated request.'
    }

    $created = Invoke-Redis -Arguments @(
        'FT.CREATE', 'smoke-index', 'ON', 'HASH', 'PREFIX', '1', 'smoke:',
        'SCHEMA', 'embedding', 'VECTOR', 'FLAT', '6',
        'TYPE', 'FLOAT32', 'DIM', '2', 'DISTANCE_METRIC', 'COSINE'
    )
    if ($created -ne 'OK') {
        throw "Vector index creation failed: $created"
    }

    $inserted = Invoke-Redis -Arguments @(
        'EVAL',
        "return redis.call('HSET', 'smoke:1', 'embedding', string.char(0,0,128,63,0,0,0,0))",
        '0'
    )
    if ($inserted -ne '1') {
        throw 'The test vector was not stored.'
    }

    $query = @'
return cjson.encode(redis.call(
    'FT.SEARCH', 'smoke-index', '*=>[KNN 1 @embedding $vector AS score]',
    'PARAMS', '2', 'vector', string.char(0,0,128,63,0,0,0,0),
    'RETURN', '1', 'score', 'DIALECT', '2'
))
'@
    $result = (Invoke-Redis -Arguments @('EVAL', $query, '0')) | ConvertFrom-Json
    if ($result[0] -ne 1 -or $result[1] -ne 'smoke:1' -or [Math]::Abs([double]$result[2][1]) -gt 0.000001) {
        throw 'Vector search did not return the matching document with zero cosine distance.'
    }

    Write-Output 'Passed: authentication required, vector index created, and nearest-neighbor search returned the expected document.'
}
finally {
    & docker rm --force $containerId | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to remove smoke-test container $containerId."
    }
}
