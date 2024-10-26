# Start the first process
exec ./mediamtx  &
# Start the second process
ffmpeg -re -stream_loop -1 -i /loop.mp4 -f rtsp -rtsp_transport tcp rtsp://localhost:8554/cam1
# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
