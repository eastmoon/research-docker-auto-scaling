## Declare alias
api() {
  curl -s http://autoworker/value
}
## Execute script
### Declare variavle
i=1
c=()
worker_ip=($(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(isa infra ps | grep autoworker | awk '{print $1}')))
worker_length=${#worker_ip[@]}
for (( w=0; w < ${worker_length}; w++ )); do
    echo "Worker ${w} IP : ${worker_ip[w]}"
done
### Execute test loop
t1=$(date +%s)
while [ $i -le 1000 ]; do
  tmp=$(api)
  ((i++)) # Increment i
  for (( w=0; w < ${worker_length}; w++ )); do
      [ $(echo ${tmp} | grep ${worker_ip[w]} | wc -l) -eq 1 ] && ((c[w]++)) || true
  done
done
t2=$(date +%s)
d=$(( t2-t1 ))
### Show result
for (( w=0; w < ${worker_length}; w++ )); do
    echo "Worker ${w} : ${c[w]}"
done
echo "total execute ${d} seconds"
