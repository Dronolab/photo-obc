echo " "
echo "_______________________________________________________" >> /var/log/mavproxy-obc.log
MSG="MAVProxy is started and modules loaded."
echo $MSG ; echo $MSG >> /var/log/mavproxy-obc.log
MSG="Log here /var/log/mavproxy-obc.log"
echo $MSG ; echo $MSG >> /var/log/mavproxy-obc.log
date >> /var/log/mavproxy-obc.log
nohup /usr/bin/python /usr/local/bin/mavproxy.py --master=/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0 --baudrate=921600 --load-module obc --daemon --show-errors >>/var/log/mavproxy-obc.log 2>&1 &
MSG="MAVProxy started PID $!"
echo $MSG ; echo $MSG >> /var/log/mavproxy-obc.log
