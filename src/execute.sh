SRC_FILENAME=1.png
DST_FILENAME=1_result.png
SENDER_LOG_FILENAME=sender_log.txt
RECEIVER_LOG_FILENAME=receiver_log.txt


echo 'remove the log and dst file'
rm -rf $SENDER_LOG_FILENAME $RECEIVER_LOG_FILENAME $DST_FILENAME

echo 'excecute'
sudo python execute_mn.py 40 $SRC_FILENAME $DST_FILENAME