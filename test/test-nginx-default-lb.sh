## Declare alias
isa() {
  curl -s http://loadbalancer/
}
## Execute script
### Declare variavle
i=1
c1=0
c2=0
### Execute test loop
t1=$(date +%s)
while [ $i -le 1000 ]; do
  tmp=$(isa)
  ((i++)) # Increment i
  [ $(echo ${tmp} | grep worker1 | wc -l) -eq 1 ] && ((c1++)) || true # Increment c1
  [ $(echo ${tmp} | grep worker2 | wc -l) -eq 1 ] && ((c2++)) || true # Increment c2
done
t2=$(date +%s)
d=$(( t2-t1 ))
### Show result
echo "Worker 1 : ${c1}"
echo "Worker 2 : ${c2}"
echo "total execute ${d} seconds"
