# Deploy the lead notifier (form -> ntfy) + the patched index.html to the BCC droplet.
# Run from anywhere:  powershell -File C:\ventures\Claw\super-claw-bros-marketing\bcc-site\lead_notify\deploy_lead.ps1
# Idempotent: safe to rerun. Backs up the nginx vhost to /root/ before touching it.
$ErrorActionPreference = "Stop"
$key  = "$HOME\.ssh\tob_deploy"
$host_ = "root@68.183.19.160"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$site = Split-Path -Parent $here
$topic = $env:S6_NTFY_TOPIC; if (-not $topic) { $topic = $env:FN_NTFY_TOPIC }
if (-not $topic) { throw "No ntfy topic in S6_NTFY_TOPIC / FN_NTFY_TOPIC (same topic notify.py uses)" }

ssh -i $key $host_ "mkdir -p /opt/bcc_lead && cp -n /etc/nginx/sites-enabled/buffaloclawmachines.com.conf /root/buffaloclawmachines.com.conf.bak; echo ok"
if ($LASTEXITCODE -ne 0) { throw "ssh failed (key present? fail2ban?)" }
scp -q -i $key "$here\bcc_lead.py"          "${host_}:/opt/bcc_lead/bcc_lead.py"
scp -q -i $key "$here\bcc_lead.service"     "${host_}:/etc/systemd/system/bcc_lead.service"
scp -q -i $key "$here\nginx_location.conf"  "${host_}:/root/bcc_lead_location.conf"
scp -q -i $key "$site\index.html"           "${host_}:/home/bccsite/htdocs/buffaloclawmachines.com/index.html"

$remote = @'
set -e
printf "NTFY_TOPIC=__TOPIC__\n" > /etc/bcc_lead.env; chmod 640 /etc/bcc_lead.env; chown root:bccsite /etc/bcc_lead.env
chmod 755 /opt/bcc_lead; chmod 644 /opt/bcc_lead/bcc_lead.py
chown bccsite:bccsite /home/bccsite/htdocs/buffaloclawmachines.com/index.html
touch /home/bccsite/logs/lead.log; chown bccsite:bccsite /home/bccsite/logs/lead.log
systemctl daemon-reload; systemctl enable bcc_lead >/dev/null 2>&1; systemctl restart bcc_lead; sleep 1
echo "service: $(systemctl is-active bcc_lead)"
C=/etc/nginx/sites-enabled/buffaloclawmachines.com.conf
if ! grep -q "location = /api/lead" "$C"; then
  python3 -c "
c=open('$C').read(); snip=open('/root/bcc_lead_location.conf').read()
m='  include /etc/nginx/global_settings;'
assert c.count(m)==1, 'vhost marker not found'
open('$C','w').write(c.replace(m, snip+'\n'+m))"
  echo "nginx: location added"
else
  echo "nginx: location already present"
fi
nginx -t 2>&1 | tail -1; systemctl reload nginx
echo "health: $(curl -s http://127.0.0.1:8580/health)"
echo "site:   $(curl -s -o /dev/null -w '%{http_code}' https://buffaloclawmachines.com/)"
echo "test:   $(curl -s -X POST https://buffaloclawmachines.com/api/lead -H 'Content-Type: application/json' -d '{"name":"Test Person","email":"test@example.com"}')"
echo "ping:   $(curl -s -X POST https://buffaloclawmachines.com/api/lead -H 'Content-Type: application/json' -d '{"name":"Deploy check","business_or_event":"bcc_lead is live","phone":"7164721689","details":"If you can read this on your phone, form leads now reach you directly."}')"
tail -3 /home/bccsite/logs/lead.log
'@
$remote = $remote.Replace("__TOPIC__", $topic) -replace "`r`n", "`n"
$tmp = [IO.Path]::GetTempFileName()
[IO.File]::WriteAllText($tmp, $remote)
scp -q -i $key $tmp "${host_}:/root/bcc_lead_deploy.sh"
Remove-Item $tmp
ssh -i $key $host_ "bash /root/bcc_lead_deploy.sh; rm -f /root/bcc_lead_deploy.sh /root/bcc_lead_location.conf"
if ($LASTEXITCODE -ne 0) { throw "remote deploy step failed" }
Write-Host "`nDone. Expect a 'New lead: Deploy check' notification on your phone." -ForegroundColor Green
