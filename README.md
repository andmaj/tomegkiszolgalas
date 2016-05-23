# tömegkiszolgálás segédprogramok

## menetrendbol_indulasok.py

A BKK GTFS menetrendjéből egy járat indulási idejeit veszi ki.

### Példa
```menetrendbol_indulasok.py -g gtfs -r 97E -m "Örs vezér tere M+H" \
-f "Erzsébet körút" -s 20160523 -e 20160619 -o 97E_4het.txt```

## indulasbol_idok.py

Indulási időbélyegekből csinál abszolút idejű
(kezdeti időhöz képest eltelt percek száma) és idődifferencia 
(indulások között eltelt percek száma) fájlokat.

### Példa

```indulasbol_idok.py -i 97E_4het.txt -s 20160523 \
-a 97E_4het_abstime.csv -d 97E_4het_difftime.csv```

## print_timestamps.py

Prints timestamps from the MRT format.

```wget ftp://routeviews.org/route-views.sydney/bgpdata/2016.05/UPDATES/updates.20160501.*
ls updates* | sort > filelist.txt
./print_mrt_timestamps.py -f filelist.txt -t ts.txt -a abs.txt -d diff.txt```

## Példa
