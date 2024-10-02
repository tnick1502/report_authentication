docker system prune -a -f
docker rm $(docker ps -a -q) -f
docker rmi $(docker images -a -q) -f
cd /root/report_autification_front
git pull
sudo service docker restart
docker-compose up