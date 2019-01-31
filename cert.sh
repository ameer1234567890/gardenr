#!/bin/sh

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root (use sudo)"
  exit 1
fi

systemctl stop gardenr.service

if [ -d /etc/letsencrypt/live/gardenr.ameer.io ]; then
  sudo certbot renew --standalone --renew-hook "sh -c 'exit 100'"
  status="$?"
  if [ "$status" -eq 0 ]; then
    status="0"
  fi
else
  sudo certbot certonly --standalone -d gardenr.ameer.io -m ameer1234567890@gmail.com --agree-tos
  status="$?"
fi

if [ "$status" -eq 0 ]; then
  cat /etc/letsencrypt/live/gardenr.ameer.io/cert.pem > gardenr.pem
  cat /etc/letsencrypt/live/gardenr.ameer.io/privkey.pem >> gardenr.pem
  mv -f gardenr.pem /etc/letsencrypt/live/gardenr.ameer.io
fi

systemctl start gardenr.service
