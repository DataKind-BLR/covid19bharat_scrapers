## HTML states
# echo "---> AP"
# python scrapers.py --state_code AP > _outputs/master_output.txt

echo "---> CT"
python scrapers.py --state_code CT >> _outputs/master_output.txt

# python scrapers.py --state_code LD >> _outputs/master_output.txt

# python scrapers.py --state_code DN >> _outputs/master_output.txt

echo "---> GJ"
python scrapers.py --state_code GJ >> _outputs/master_output.txt

# python scrapers.py --state_code LA >> _outputs/master_output.txt

# python scrapers.py --state_code MH >> _outputs/master_output.txt

echo "---> ML"
python scrapers.py --state_code ML >> _outputs/master_output.txt

echo "---> OR"
# python scrapers.py --state_code OR >> _outputs/master_output.txt

# python scrapers.py --state_code PY >> _outputs/master_output.txt

echo "---> TR"
python scrapers.py --state_code TR >> _outputs/master_output.txt

echo "---> HR"
# python scrapers.py --state_code HR >> _outputs/master_output.txt -t pdf -u _inputs/hr.pdf

# python scrapers.py --state_code UP >> _outputs/master_output.txt

# python scrapers.py --state_code RJ >> _outputs/master_output.txt


## Image States (download / crop them first)
# python scrapers.py --state_code AR --type image --url _inputs/ar.jpeg >> _outputs/master_output.txt
# python scrapers.py --state_code CT --type image --url _inputs/ct.jpeg >> _outputs/master_output.txt
# python scrapers.py --state_code MP --type image --url _inputs/mp.jpeg >> _outputs/master_output.txt
# NOTE: Bihar has 2 images
# python scrapers.py --state_code BR --type image --url _inputs/br.jpeg >> _outputs/master_output.txt
# python scrapers.py --state_code BR --type image --url _inputs/br2.jpeg >> _outputs/master_output.txt

