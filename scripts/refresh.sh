#!/usr/bin/env bash
# SROTrac daily refresh: re-fetch source pages, rebuild data + site, commit & push on change.
# Designed to be run by the daily automation agent (and safe to run by hand).
set -uo pipefail
cd "$(dirname "$0")/.."

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
RAW=data/raw
fetch() { # fetch <url> <outfile>
  curl -sL --max-time 40 -A "$UA" "$1" -o "$2" && [ -s "$2" ]
}

FAILED=0
fetch "https://faceofindia.org/membership/"                "$RAW/face_membership.html" || { echo "FETCH FAIL face"; FAILED=1; }
fetch "https://unifiedfintech.in/"                          "$RAW/uff_home.html"        || { echo "FETCH FAIL uff (js-rendered, may be stale)"; }
fetch "https://srpa.org.in/"                                "$RAW/srpa_home.html"       || { echo "FETCH FAIL srpa"; FAILED=1; }
fetch "https://mfinindia.org/members"                       "$RAW/mfin_members.html"    || { echo "FETCH FAIL mfin"; FAILED=1; }
fetch "https://www.fedai.org.in/InnerPageContent.aspx?Cid=2&SCid=1&SSCid=0" "$RAW/fedai_members.html" || { echo "FETCH FAIL fedai"; FAILED=1; }
fetch "https://www.fidcindia.org.in"                        "$RAW/fidc_home.html"       || { echo "FETCH FAIL fidc home"; }
fetch "https://www.sa-dhan.net"                             "$RAW/sadhan_home.html"     || { echo "FETCH FAIL sadhan home"; }
fetch "https://sahamati.org.in"                             "$RAW/sahamati_home.html"   || { echo "FETCH FAIL sahamati home"; }
fetch "https://www.fimmda.org"                              "$RAW/fimmda_home.html"     || { echo "FETCH FAIL fimmda home"; }
# homepage snapshots backing the social-presence drift check (failures non-fatal:
# a stale snapshot keeps the previous handle, the check just skips a beat)
fetch "https://www.fidcindia.org.in"                        "$RAW/fidc_home.html"       || { echo "FETCH FAIL fidc home"; }
fetch "https://www.sa-dhan.net"                             "$RAW/sadhan_home.html"     || { echo "FETCH FAIL sadhan home"; }
fetch "https://sahamati.org.in"                             "$RAW/sahamati_home.html"   || { echo "FETCH FAIL sahamati home"; }
fetch "https://www.fimmda.org"                              "$RAW/fimmda_home.html"     || { echo "FETCH FAIL fimmda home"; }

python3 scripts/build.py  || exit 1
python3 scripts/site.py   || exit 1
python3 scripts/bloggen.py || exit 1
python3 scripts/social_check.py || echo "SOCIAL CHECK FAIL (non-fatal)"
python3 scripts/social_check.py || echo "SOCIAL CHECK FAIL (non-fatal)"

if [ -n "$(git status --porcelain -- data docs ':(exclude)data/raw' blog *.html css js)" ]; then
  git add -A
  git -c user.name="SROTrac bot" -c user.email="cashlessconsumerin@gmail.com" \
    commit -q -m "Daily refresh $(date -u +%F-%H%M) UTC — source re-fetch + rebuild"
  git push -q origin main && echo "PUSHED: changes found and deployed"
else
  echo "NO-CHANGE: rosters and content unchanged"
fi
[ "$FAILED" = "0" ] && echo "REFRESH OK" || echo "REFRESH DONE (with fetch failures)"
