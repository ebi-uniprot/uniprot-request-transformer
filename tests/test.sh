testout=./tests/test.txt
input=./tests/input.txt
expected=./tests/expected.txt
cat ./tests/input.txt | ./transformer.py > $testout
if cmp --silent -- $expected $testout; then
  echo "PASS"
else
  echo "FAIl"
  diff -u $expected $testout 
fi