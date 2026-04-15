#!/bin/bash
echo "=========================================="
echo "SDRangel Multi-Instance Status"
echo "=========================================="
echo ""

for port in 8091 8092 8093; do
  case $port in
    8091) label="ADS-B Aircraft"; svc="sdrangel-adsb" ;;
    8092) label="Marine/AIS/WX/Railroad"; svc="sdrangel-marine" ;;
    8093) label="Aviation/FM (switchable)"; svc="sdrangel-aviation" ;;
  esac
  svc_status=$(systemctl is-active $svc.service 2>/dev/null)
  echo "--- Port $port: $label ($svc_status) ---"
  if [ "$svc_status" = "active" ]; then
    curl -s -m 5 "http://localhost:$port/sdrangel/deviceset/0" 2>/dev/null | python3 /home/dragon/sdrangel-status-helper.py
  fi
  echo ""
done

echo "=========================================="
echo "Switching commands (for port 8093 E4000):"
echo "  Aviation mode:  ~/sdrangel-load-aviation.sh"
echo "  FM Band 1 (KNKX/KEXP/KBCS):      ~/sdrangel-load-fm.sh 1"
echo "  FM Band 2 (KMPS/KUOW/KJR/KJAQ):   ~/sdrangel-load-fm.sh 2"
echo "  FM Band 3 (KIRO/KING/KISW):        ~/sdrangel-load-fm.sh 3"
echo "  FM Band 4 (KQMV/KPLZ/KZOK):       ~/sdrangel-load-fm.sh 4"
echo "  FM Band 5 (KISS/KNDD):             ~/sdrangel-load-fm.sh 5"
echo "=========================================="
