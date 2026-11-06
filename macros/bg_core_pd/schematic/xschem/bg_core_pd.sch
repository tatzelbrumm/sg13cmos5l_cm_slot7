v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 10 5 140 -1070 380 -1070 380 -115 140 -115 140 -1070 {dash=6}
P 10 5 1330 -1070 1450 -1070 1450 -115 1330 -115 1330 -1070 {dash=6}
P 10 5 400 -1070 1310 -1070 1310 -115 400 -115 400 -1070 {dash=6}
P 10 5 165 -255 255 -255 255 -135 165 -135 165 -255 {dash=6}
P 10 5 780 -965 854 -965 854 -875 780 -875 780 -965 {dash=6}
T {bg_core_pd: reference-current core of bias_bg_pd, cut from that flat sheet (core devices and their wiring only).} 60 -1190 0 0 0.3 0.3 {}
T {iout: the core output (POC drain) into the tree input; en_3v3 / en_3v3_b: enable and its complement (from inv_3v3_pd).} 60 -1164 0 0 0.3 0.3 {}
T {Disabled: MS1 off (gate en_3v3_b), SKS pulls ks to vss, SVPG pulls vpg to vdd, so PO / POC are off and iout is high-Z.} 60 -1138 0 0 0.3 0.3 {}
T {Source: bias_ref_pd.spice} 60 -1112 0 0 0.3 0.3 {}
T {[S] start-up} 145 -1090 0 0 0.3 0.3 {layer=10}
T {[R] output, I_ref} 1335 -1090 0 0 0.3 0.3 {layer=10}
T {[C] bandgap core} 405 -1090 0 0 0.3 0.3 {layer=10}
T {[E] enable} 165 -280 0 0 0.3 0.3 {layer=10}
T {[E] enable} 785 -990 0 0 0.3 0.3 {layer=10}
N 240 -440 260 -440 {lab=vss}
N 260 -560 300 -560 {lab=ks}
N 340 -720 340 -590 {lab=vpc}
N 340 -560 360 -560 {lab=vss}
N 360 -560 360 -100 {lab=vss}
N 500 -920 500 -860 {lab=vpg}
N 460 -890 460 -860 {lab=vpg}
N 460 -1000 460 -950 {lab=vdd}
N 440 -920 460 -920 {lab=vdd}
N 440 -1000 440 -920 {lab=vdd}
N 500 -800 500 -740 {lab=vpc}
N 460 -740 500 -740 {lab=vpc}
N 460 -770 460 -740 {lab=vpc}
N 460 -860 460 -830 {lab=vpg}
N 440 -800 460 -800 {lab=vdd}
N 440 -920 440 -800 {lab=vdd}
N 440 -440 460 -440 {lab=vss}
N 460 -410 460 -380 {lab=eb}
N 750 -200 750 -100 {lab=vss}
N 1010 -1000 1010 -950 {lab=vdd}
N 1010 -920 1030 -920 {lab=vdd}
N 1030 -1000 1030 -920 {lab=vdd}
N 1010 -800 1030 -800 {lab=vdd}
N 1030 -920 1030 -800 {lab=vdd}
N 970 -500 970 -440 {lab=g}
N 970 -500 1010 -500 {lab=g}
N 1010 -440 1030 -440 {lab=vss}
N 930 -380 1010 -380 {lab=ea}
N 970 -200 970 -100 {lab=vss}
N 500 -500 500 -440 {lab=g}
N 500 -500 970 -500 {lab=g}
N 1410 -1000 1410 -950 {lab=vdd}
N 1410 -920 1430 -920 {lab=vdd}
N 1430 -1000 1430 -920 {lab=vdd}
N 1410 -890 1410 -830 {lab=co}
N 1410 -800 1430 -800 {lab=vdd}
N 1430 -920 1430 -800 {lab=vdd}
N 970 -920 970 -860 {lab=vpg}
N 970 -800 970 -740 {lab=vpc}
N 1370 -920 1370 -860 {lab=vpg}
N 1370 -800 1370 -740 {lab=vpc}
N 1010 -500 1010 -470 {lab=g}
N 930 -170 930 -100 {lab=vss}
N 790 -170 790 -100 {lab=vss}
N 1010 -410 1010 -380 {lab=ea}
N 930 -380 930 -230 {lab=ea}
N 1030 -440 1030 -100 {lab=vss}
N 440 -440 440 -100 {lab=vss}
N 340 -530 340 -100 {lab=vss}
N 460 -860 500 -860 {lab=vpg}
N 460 -720 460 -470 {lab=vpc}
N 260 -410 260 -100 {lab=vss}
N 260 -520 260 -470 {lab=ks}
N 300 -500 300 -440 {lab=g}
N 260 -1000 280 -1000 {lab=vdd}
N 850 -1000 1010 -1000 {lab=vdd}
N 440 -1000 460 -1000 {lab=vdd}
N 1010 -1000 1030 -1000 {lab=vdd}
N 240 -100 260 -100 {lab=vss}
N 260 -100 340 -100 {lab=vss}
N 340 -100 360 -100 {lab=vss}
N 460 -100 750 -100 {lab=vss}
N 440 -100 460 -100 {lab=vss}
N 750 -100 790 -100 {lab=vss}
N 790 -100 930 -100 {lab=vss}
N 930 -100 970 -100 {lab=vss}
N 1010 -100 1030 -100 {lab=vss}
N 280 -1000 440 -1000 {lab=vdd}
N 1010 -890 1010 -830 {lab=ca}
N 360 -100 440 -100 {lab=vss}
N 1010 -770 1010 -500 {lab=g}
N 340 -720 460 -720 {lab=vpc}
N 460 -740 460 -720 {lab=vpc}
N 300 -500 500 -500 {lab=g}
N 220 -520 220 -230 {lab=ks}
N 220 -520 260 -520 {lab=ks}
N 220 -170 220 -100 {lab=vss}
N 220 -200 240 -200 {lab=vss}
N 240 -200 240 -100 {lab=vss}
N 220 -100 240 -100 {lab=vss}
N 830 -1000 830 -950 {lab=vdd}
N 830 -920 850 -920 {lab=vdd}
N 850 -1000 850 -920 {lab=vdd}
N 830 -890 830 -860 {lab=vpg}
N 830 -1000 850 -1000 {lab=vdd}
N 500 -860 830 -860 {lab=vpg}
N 460 -1000 830 -1000 {lab=vdd}
N 240 -440 240 -200 {lab=vss}
N 260 -560 260 -520 {lab=ks}
N 790 -920 790 -680 {lab=en_3v3}
N 180 -580 180 -200 {lab=en_3v3_b}
N 970 -100 1010 -100 {lab=vss}
N 1410 -1000 1430 -1000 {lab=vdd}
N 970 -740 1370 -740 {lab=vpc}
N 500 -740 970 -740 {lab=vpc}
N 970 -860 1370 -860 {lab=vpg}
N 830 -860 970 -860 {lab=vpg}
N 1030 -1000 1410 -1000 {lab=vdd}
N 1410 -770 1410 -620 {lab=iout}
N 1410 -620 1470 -620 {}
N 100 -1000 260 -1000 {lab=vdd}
N 100 -100 220 -100 {lab=vss}
N 100 -680 790 -680 {lab=en_3v3}
N 100 -580 180 -580 {lab=en_3v3_b}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 280 -440 0 1 {name=MS2
l=1u
w=10u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 320 -560 0 0 {name=MS3
l=2u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 480 -920 0 1 {name=PB
l=1u
w=40u
ng=4
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 480 -800 0 1 {name=PBC
l=1u
w=40u
ng=4
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 480 -440 0 1 {name=NB
l=4u
w=20u
ng=2
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
C {sg13cmos5l_pr/pnpMPA.sym} 770 -200 0 0 {name=Q2
model=pnpMPA
spiceprefix=X
w=2e-6
l=2e-6
m=8}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 990 -920 0 0 {name=PA
l=1u
w=40u
ng=4
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 990 -800 0 0 {name=PAC
l=1u
w=40u
ng=4
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {devices/lab_wire.sym} 1010 -865 0 0 {name=l4 sig_type=std_logic lab=ca}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 990 -440 0 0 {name=NA
l=4u
w=20u
ng=2
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
C {sg13cmos5l_pr/pnpMPA.sym} 950 -200 0 1 {name=Q1
model=pnpMPA
spiceprefix=X
w=2e-6
l=2e-6
m=1}
C {devices/lab_wire.sym} 1010 -395 0 0 {name=l5 sig_type=std_logic lab=ea}
C {devices/lab_wire.sym} 1010 -700 0 0 {name=l6 sig_type=std_logic lab=g}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1390 -920 0 0 {name=PO
l=1u
w=80u
ng=8
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1390 -800 0 0 {name=POC
l=1u
w=80u
ng=8
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {devices/lab_wire.sym} 1410 -865 0 0 {name=l7 sig_type=std_logic lab=co}
C {devices/lab_wire.sym} 460 -875 0 1 {name=l9 sig_type=std_logic lab=vpg}
C {devices/lab_wire.sym} 460 -725 0 1 {name=l10 sig_type=std_logic lab=vpc}
C {devices/iopin.sym} 100 -1000 0 1 {name=p1 lab=vdd}
C {devices/iopin.sym} 100 -100 0 1 {name=p2 lab=vss}
C {devices/ipin.sym} 100 -680 0 0 {name=p11 lab=en_3v3}
C {devices/lab_wire.sym} 180 -580 0 1 {name=l19 sig_type=std_logic lab=en_3v3_b}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 200 -200 0 0 {name=SKS
l=0.45u
w=1u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 810 -920 0 0 {name=SVPG
l=0.45u
w=1u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {devices/ipin.sym} 100 -580 0 0 {name=p13 lab=en_3v3_b}
C {devices/opin.sym} 1470 -620 0 0 {name=p14 lab=iout}
C {devices/title.sym} 160 -40 0 0 {name=l0 author="Christoph Maier"}
C {devices/lab_wire.sym} 460 -380 0 0 {name=l2 sig_type=std_logic lab=eb}
N 260 -620 260 -560 {lab=ks}
C {devices/lab_wire.sym} 260 -620 0 0 {name=l1 sig_type=std_logic lab=ks}
T {MS1 (0.5u / 100u) is drawn as} 150 -960 0 0 0.2 0.2 {}
T {8 x 0.5u / 12.5u in series: [S1]} 150 -942 0 0 0.2 0.2 {}
C {sg13cmos5l_pr/rhigh.sym} 580 -320 0 0 {name=R1B[9:0]
w=0.5u
l=9.94u
model=rhigh
body=vss
spiceprefix=X
b=0
m=1
mm_ok=1}
C {devices/lab_pin.sym} 580 -350 0 0 {name=l_r1b_p sig_type=std_logic lab=eb,n1b[8:0]}
C {devices/lab_pin.sym} 580 -290 0 0 {name=l_r1b_m sig_type=std_logic lab=n1b[8:0],vss}
C {sg13cmos5l_pr/rhigh.sym} 790 -320 0 0 {name=R0[17:0]
w=0.5u
l=9.94u
model=rhigh
body=vss
spiceprefix=X
b=0
m=1
mm_ok=1}
C {devices/lab_pin.sym} 790 -350 0 0 {name=l_r0_p sig_type=std_logic lab=eb,n0[16:0]}
C {devices/lab_pin.sym} 790 -290 0 0 {name=l_r0_m sig_type=std_logic lab=n0[16:0],e2}
C {sg13cmos5l_pr/rhigh.sym} 1170 -320 0 0 {name=R1A[10:0]
w=0.5u
l=9.94u
model=rhigh
body=vss
spiceprefix=X
b=0
m=1
mm_ok=1}
C {devices/lab_pin.sym} 1170 -350 0 0 {name=l_r1a_p sig_type=std_logic lab=ea,n1a[9:0]}
C {devices/lab_pin.sym} 1170 -290 0 0 {name=l_r1a_m sig_type=std_logic lab=n1a[9:0],vss}
N 790 -230 790 -250 {lab=e2}
C {devices/lab_pin.sym} 790 -250 0 1 {name=l_e2 sig_type=std_logic lab=e2}
T {R0, R1A, R1B as drawn (compact layout): chains of 18 / 11 / 10 rhigh} 480 -656 0 0 0.2 0.2 {}
T {segments 0.5u / 9.94u, as vector instances R0[17:0], R1A[10:0], R1B[9:0];} 480 -638 0 0 0.2 0.2 {}
T {the bus labels name the chain nodes (eb, n0[16] ... n0[0], e2).} 480 -620 0 0 0.2 0.2 {}
T {Each segment has its own heads: R +0.70 % (R0), +1.03 % (R1A), +1.02 % (R1B)} 480 -602 0 0 0.2 0.2 {}
T {against the single devices 0.5u / 179.5u, 109.3u, 99.36u.} 480 -584 0 0 0.2 0.2 {}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -960 0 0 {name=MS1_0
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -960 1640 -960 {lab=en_3v3_b}
N 1680 -960 1700 -960 {lab=vdd}
N 1680 -930 1680 -910 {lab=ms1_1}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -880 0 0 {name=MS1_1
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -880 1640 -880 {lab=en_3v3_b}
N 1680 -880 1700 -880 {lab=vdd}
N 1680 -850 1680 -830 {lab=ms1_2}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -800 0 0 {name=MS1_2
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -800 1640 -800 {lab=en_3v3_b}
N 1680 -800 1700 -800 {lab=vdd}
N 1680 -770 1680 -750 {lab=ms1_3}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -720 0 0 {name=MS1_3
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -720 1640 -720 {lab=en_3v3_b}
N 1680 -720 1700 -720 {lab=vdd}
N 1680 -690 1680 -670 {lab=ms1_4}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -640 0 0 {name=MS1_4
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -640 1640 -640 {lab=en_3v3_b}
N 1680 -640 1700 -640 {lab=vdd}
N 1680 -610 1680 -590 {lab=ms1_5}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -560 0 0 {name=MS1_5
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -560 1640 -560 {lab=en_3v3_b}
N 1680 -560 1700 -560 {lab=vdd}
N 1680 -530 1680 -510 {lab=ms1_6}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -480 0 0 {name=MS1_6
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -480 1640 -480 {lab=en_3v3_b}
N 1680 -480 1700 -480 {lab=vdd}
N 1680 -450 1680 -430 {lab=ms1_7}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1660 -400 0 0 {name=MS1_7
l=12.5u
w=0.5u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 1620 -400 1640 -400 {lab=en_3v3_b}
N 1680 -400 1700 -400 {lab=vdd}
N 1620 -960 1620 -400 {lab=en_3v3_b}
C {devices/lab_pin.sym} 1620 -960 0 0 {name=l_s1_g sig_type=std_logic lab=en_3v3_b}
N 1680 -990 1680 -1010 {lab=vdd}
N 1680 -1010 1700 -1010 {lab=vdd}
N 1700 -1010 1700 -400 {lab=vdd}
C {devices/lab_pin.sym} 1700 -1010 0 1 {name=l_s1_vdd sig_type=std_logic lab=vdd}
N 1680 -370 1680 -340 {lab=ks}
C {devices/lab_pin.sym} 1680 -340 0 1 {name=l_s1_ks sig_type=std_logic lab=ks}
P 10 5 1560 -1070 1770 -1070 1770 -280 1560 -280 1560 -1070 {dash=6}
T {[S1] MS1 as drawn} 1565 -1110 0 0 0.3 0.3 {layer=10}
T {8 x 0.5u / 12.5u, vdd to ks, gates en_3v3_b} 1565 -1088 0 0 0.2 0.2 {layer=10}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1900 -960 0 0 {name=MDUM0
l=1u
w=2.4u
ng=8
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {devices/lab_pin.sym} 1880 -960 0 0 {name=l_mdum0_g sig_type=std_logic lab=vpg}
N 1920 -990 1940 -990 {lab=vdd}
N 1920 -960 1940 -960 {lab=vdd}
N 1920 -930 1940 -930 {lab=vdd}
N 1940 -990 1940 -930 {lab=vdd}
C {devices/lab_pin.sym} 1940 -990 0 1 {name=l_mdum0_r sig_type=std_logic lab=vdd}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 1900 -820 0 0 {name=MDUM1
l=1u
w=2.4u
ng=8
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
C {devices/lab_pin.sym} 1880 -820 0 0 {name=l_mdum1_g sig_type=std_logic lab=vpc}
N 1920 -850 1940 -850 {lab=vdd}
N 1920 -820 1940 -820 {lab=vdd}
N 1920 -790 1940 -790 {lab=vdd}
N 1940 -850 1940 -790 {lab=vdd}
C {devices/lab_pin.sym} 1940 -850 0 1 {name=l_mdum1_r sig_type=std_logic lab=vdd}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 1900 -660 0 0 {name=MDUM2
l=1u
w=2u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 1880 -660 1860 -660 {lab=g}
N 1920 -690 1920 -710 {lab=g}
N 1920 -710 1860 -710 {lab=g}
N 1860 -710 1860 -610 {lab=g}
N 1920 -630 1920 -610 {lab=g}
N 1920 -610 1860 -610 {lab=g}
C {devices/lab_pin.sym} 1860 -710 0 0 {name=l_mdum2_g sig_type=std_logic lab=g}
N 1920 -660 1940 -660 {lab=vss}
N 1940 -660 1940 -590 {lab=vss}
C {devices/lab_pin.sym} 1940 -590 0 1 {name=l_mdum2_b sig_type=std_logic lab=vss}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 1900 -500 0 0 {name=MDUM3
l=4u
w=16u
ng=8
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 1880 -500 1860 -500 {lab=g}
N 1920 -530 1920 -550 {lab=g}
N 1920 -550 1860 -550 {lab=g}
N 1860 -550 1860 -450 {lab=g}
N 1920 -470 1920 -450 {lab=g}
N 1920 -450 1860 -450 {lab=g}
C {devices/lab_pin.sym} 1860 -550 0 0 {name=l_mdum3_g sig_type=std_logic lab=g}
N 1920 -500 1940 -500 {lab=vss}
N 1940 -500 1940 -430 {lab=vss}
C {devices/lab_pin.sym} 1940 -430 0 1 {name=l_mdum3_b sig_type=std_logic lab=vss}
C {sg13cmos5l_pr/rhigh.sym} 1900 -320 0 0 {name=RDUM[1:0]
w=0.5u
l=9.94u
model=rhigh
body=vss
spiceprefix=X
b=0
m=1
mm_ok=1}
C {devices/lab_pin.sym} 1900 -350 0 0 {name=l_rdum_p sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1900 -290 0 0 {name=l_rdum_m sig_type=std_logic lab=vss}
P 10 5 1810 -1070 2110 -1070 2110 -200 1810 -200 1810 -1070 {dash=6}
T {[D] dummies of the layout} 1815 -1132 0 0 0.3 0.3 {layer=10}
T {PMOS: D = S = bulk = vdd, gates vpg / vpc} 1815 -1110 0 0 0.2 0.2 {layer=10}
T {NMOS: D = S = G = g (Vgs = 0), bulk vss; rhigh: both ends vss} 1815 -1092 0 0 0.2 0.2 {layer=10}
T {Since 2026-10-28 backannotated from the compact layout (layout/gds/bg_core_pd.gds): resistors as chains [C], NA / NB ng 2 (W, L as before), MS1 as drawn [S1], dummies [D].} 60 -1216 0 0 0.3 0.3 {}
