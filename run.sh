#!/usr/bin/sh

helpFunc()
{
  echo ""
  echo "Usage: $0 [options] ... [ -s SERVER_PROGRAM | -i IP_ADDRESS | -p PORT | -r | -h ] ..."
  echo "Options and arguments (and corresponding environment variables):"
  echo -e "\t-s   : Name of ASGI server program to run a server, can be 'hypercorn' or 'uvicorn' but the default one is hypercorn"
  echo -e "\t-i   : IPv4 of the server, default is 127.0.0.1"
  echo -e "\t-p   : Port of the server, default is 6410"
  echo -e "\t-r   : Reload the server again whenever it terminate itself from failure"
  echo -e "\t-h   : Show this help"
  exit 1
}

while getopts "s:i:p:rh" opt
do
  case "$opt" in
    s ) server_program="$OPTARG" ;;
    i ) ip="$OPTARG" ;;
    p ) port="$OPTARG" ;;
    r ) reload="--reload" ;;
    h ) helpFunc ;;
  esac
done

[ -z "$server_program" ] && server_program="hypercorn"
[ -z "$ip" ] && ip="127.0.0.1"
[ -z "$port" ] && port="6410"

[ "$server_program" == "hypercorn" ] && hypercorn main:server --bind "$ip:$port" $reload
[ "$server_program" == "uvicorn" ] && uvicorn main:server --host $ip --port $port $reload
