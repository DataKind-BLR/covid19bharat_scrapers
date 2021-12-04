## HTML states
python scrapers.py --state_code AP > _outputs/master_output.txt
python scrapers.py --state_code CH >> _outputs/master_output.txt
python scrapers.py --state_code LD >> _outputs/master_output.txt
python scrapers.py --state_code DN >> _outputs/master_output.txt
python scrapers.py --state_code GJ >> _outputs/master_output.txt
python scrapers.py --state_code LA >> _outputs/master_output.txt
# python scrapers.py --state_code MH >> _outputs/master_output.txt
python scrapers.py --state_code ML >> _outputs/master_output.txt
python scrapers.py --state_code OR >> _outputs/master_output.txt
python scrapers.py --state_code PY >> _outputs/master_output.txt
python scrapers.py --state_code TR >> _outputs/master_output.txt


## PDF States (download them first)
pytnon scrapers.py --state_code HR --type pdf --url _inputs/hr.pdf >> _outputs/master_output.txt


## Image States (download / crop them first)
python scrapers.py --state_code AR --type image --url _inputs/ar.jpeg >> _outputs/master_output.txt
python scrapers.py --state_code CT --type image --url _inputs/ct.jpeg >> _outputs/master_output.txt
python scrapers.py --state_code MP --type image --url _inputs/mp.jpeg >> _outputs/master_output.txt
# NOTE: Bihar has 2 images
python scrapers.py --state_code BR --type image --url _inputs/br.jpeg >> _outputs/master_output.txt
python scrapers.py --state_code BR --type image --url _inputs/br2.jpeg >> _outputs/master_output.txt

