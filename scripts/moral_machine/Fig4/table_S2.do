*This file creates table S2

use "data\DataEdmond_tableS2.dta", replace


eststo: reg distance new_relgendist_weighted_usa geodesicdistUSA, r
eststo: reg distance m_culturaldistancefromus geodesicdistUSA, r
esttab using distance.rtf, replace star(* 0.10 ** 0.05 *** 0.01) r2 se cells(b(star fmt(2)) se(par fmt(3))) scalars(F)
eststo clear
