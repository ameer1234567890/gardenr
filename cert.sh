#!/bin/sh

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root (use sudo)"
  exit 1
fi

systemctl stop gardenr.service

if [ -d /etc/letsencrypt/live/gardenr.ameer.io ]; then
  sudo certbot renew --standalone --renew-hook "echo 'YES' > updated.txt"
else
  sudo certbot certonly --standalone -d gardenr.ameer.io -m ameer1234567890@gmail.com --agree-tos
  status="$?"
  if [ "$status" = "0" ]; then
    echo 'YES' > updated.txt
  fi
fi

if [ "$(cat updated.txt 2>/dev/null)" = "YES" ]; then
  rm updated.txt
  cat /etc/letsencrypt/live/gardenr.ameer.io/cert.pem > gardenr.pem
  cat /etc/letsencrypt/live/gardenr.ameer.io/privkey.pem >> gardenr.pem
  mv -f gardenr.pem /etc/letsencrypt/live/gardenr.ameer.io
fi

systemctl start gardenr.service
