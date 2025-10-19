## Declare alias
## Execute script
#
echo "----- Check and list infrastructure environment status. -----"
curl -X GET http://localhost/isa/infra
#
echo "----- Show all infrastructure container information. -----"
curl -X GET http://localhost/isa/infra/ps
#
echo "----- Show all infrastructure container resource usage statistics. -----"
curl -X GET http://localhost/isa/infra/stats
