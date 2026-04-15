#!/bin/bash
sleep 5
docker cp /home/dragon/openwebrx-config/seattle-bookmarks.html openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html 2>/dev/null
