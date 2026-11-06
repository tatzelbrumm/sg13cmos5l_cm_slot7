* NGSPICE file created from bg_core_pd.ext - technology: ihp-sg13cmos5l

.subckt bg_core_pd vdd vss iout en_3v3 en_3v3_b
X0 a_4703_6072# bg_n4_0.ea vss rhigh l=9.94u w=0.5u
X1 a_4431_6072# bg_n4_0.eb vss rhigh l=9.94u w=0.5u
X2 a_623_6072# a_1167_3998# vss rhigh l=9.94u w=0.5u
X3 a_918_8440# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X4 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=73.8615p ps=0.3643m w=2u l=4u
X5 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0.15688n ps=0.4126m w=0.3u l=1u
X6 a_918_6928# bg_n4_0.vpc iout vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X7 a_2799_6072# a_2391_3998# vss rhigh l=9.94u w=0.5u
X8 vdd bg_pmir_pcas_c_0.vpg bg_pmir_pcas_c_0.vpg vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X9 a_1847_6072# a_2391_3998# vss rhigh l=9.94u w=0.5u
X10 vdd bg_pmir_pcas_c_0.vpg a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X11 bg_n4_0.vpc bg_n4_0.vpc bg_pmir_pcas_c_0.vpg vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X12 a_4703_6072# a_4159_3998# vss rhigh l=9.94u w=0.5u
X13 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X14 a_3887_6072# a_4295_3998# vss rhigh l=9.94u w=0.5u
X15 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X16 vss en_3v3_b bg_n4_0.ks vss sg13_hv_nmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.45u
X17 vss bg_n4_0.ks bg_n4_0.vpc vss sg13_hv_nmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=2u
X18 a_2527_6072# a_2255_3998# vss rhigh l=9.94u w=0.5u
X19 a_215_6072# a_487_3998# vss rhigh l=9.94u w=0.5u
X20 vdd en_3v3 bg_pmir_pcas_c_0.vpg vdd sg13_hv_pmos ad=0.34p pd=2.68u as=0.34p ps=2.68u w=1u l=0.45u
X21 vss vss bg_n4_0.ea pnpMPA a=4p p=8u
X22 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X23 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X24 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X25 a_8390_5412# en_3v3_b a_5822_5262# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X26 a_3479_6072# a_4023_3998# vss rhigh l=9.94u w=0.5u
X27 a_3751_6072# a_3207_3998# vss rhigh l=9.94u w=0.5u
X28 vdd bg_pmir_pcas_c_0.vpg a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X29 a_215_6072# bg_pnp_c_0.e2 vss rhigh l=9.94u w=0.5u
X30 bg_pmir_pcas_c_0.vpg bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X31 a_8390_5712# en_3v3_b a_5822_5562# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X32 a_1575_6072# a_1167_3998# vss rhigh l=9.94u w=0.5u
X33 a_918_8440# bg_n4_0.vpc bg_n4_0.g vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X34 bg_n4_0.ks en_3v3_b a_5822_5262# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X35 vdd bg_pmir_pcas_c_0.vpg bg_pmir_pcas_c_0.vpg vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X36 bg_n4_0.g bg_n4_0.g bg_n4_0.ea vss sg13_hv_nmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=4u
X37 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X38 a_3479_6072# a_2935_3998# vss rhigh l=9.94u w=0.5u
X39 a_2527_6072# a_3071_3998# vss rhigh l=9.94u w=0.5u
X40 iout bg_n4_0.vpc a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X41 bg_pmir_pcas_c_0.vpg bg_n4_0.vpc bg_n4_0.vpc vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X42 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X43 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X44 a_8390_5412# en_3v3_b a_5822_5562# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X45 a_1303_6072# a_1031_3998# vss rhigh l=9.94u w=0.5u
X46 a_918_6928# bg_n4_0.vpc iout vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X47 iout bg_n4_0.vpc a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X48 a_8390_6012# en_3v3_b a_5822_5862# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X49 a_918_6928# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X50 a_2799_6072# a_3207_3998# vss rhigh l=9.94u w=0.5u
X51 a_2663_6072# a_2935_3998# vss rhigh l=9.94u w=0.5u
X52 a_895_6072# a_351_3998# vss rhigh l=9.94u w=0.5u
X53 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X54 a_8390_5712# en_3v3_b a_5822_5862# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X55 bg_n4_0.g bg_n4_0.vpc a_918_8440# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X56 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X57 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X58 a_4567_6072# a_4839_3998# vss rhigh l=9.94u w=0.5u
X59 a_4431_6072# a_4023_3998# vss rhigh l=9.94u w=0.5u
X60 vdd en_3v3_b a_5822_6162# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X61 vdd bg_pmir_pcas_c_0.vpg a_918_8440# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X62 a_623_6072# vss vss rhigh l=9.94u w=0.5u
X63 a_1983_6072# a_2255_3998# vss rhigh l=9.94u w=0.5u
X64 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X65 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X66 vss bg_n4_0.g bg_n4_0.ks vss sg13_hv_nmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X67 a_1983_6072# a_1711_3998# vss rhigh l=9.94u w=0.5u
X68 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X69 a_918_6928# bg_n4_0.vpc iout vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X70 a_3751_6072# a_4159_3998# vss rhigh l=9.94u w=0.5u
X71 a_3887_6072# a_3615_3998# vss rhigh l=9.94u w=0.5u
X72 a_8390_6012# en_3v3_b a_5822_6162# vdd sg13_hv_pmos ad=0.17p pd=1.68u as=0.17p ps=1.68u w=0.5u l=12.5u
X73 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X74 a_918_6928# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X75 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X76 vss vss vss rhigh l=9.94u w=0.5u
X77 bg_pmir_pcas_c_0.vpg bg_n4_0.vpc bg_n4_0.vpc vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X78 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X79 bg_n4_0.g bg_n4_0.vpc a_918_8440# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X80 a_5111_6072# bg_n4_0.eb vss rhigh l=9.94u w=0.5u
X81 a_1303_6072# a_1711_3998# vss rhigh l=9.94u w=0.5u
X82 bg_n4_0.ea bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=4u
X83 a_3343_6072# a_3615_3998# vss rhigh l=9.94u w=0.5u
X84 iout bg_n4_0.vpc a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X85 vdd bg_pmir_pcas_c_0.vpg a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X86 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X87 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X88 vss vss vss rhigh l=9.94u w=0.5u
X89 a_895_6072# a_1439_3998# vss rhigh l=9.94u w=0.5u
X90 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X91 a_5111_6072# a_4839_3998# vss rhigh l=9.94u w=0.5u
X92 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X93 a_759_6072# a_1031_3998# vss rhigh l=9.94u w=0.5u
X94 bg_n4_0.eb bg_n4_0.g bg_n4_0.vpc vss sg13_hv_nmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=4u
X95 bg_pmir_pcas_c_0.vpg bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X96 a_918_8440# bg_n4_0.vpc bg_n4_0.g vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X97 a_2663_6072# a_2119_3998# vss rhigh l=9.94u w=0.5u
X98 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X99 a_4567_6072# a_4295_3998# vss rhigh l=9.94u w=0.5u
X100 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X101 iout bg_n4_0.vpc a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X102 vdd bg_pmir_pcas_c_0.vpg a_918_6928# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X103 a_759_6072# a_487_3998# vss rhigh l=9.94u w=0.5u
X104 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X105 vss a_351_3998# vss rhigh l=9.94u w=0.5u
X106 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=1u
X107 a_918_8440# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X108 bg_n4_0.vpc bg_n4_0.g bg_n4_0.eb vss sg13_hv_nmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=4u
X109 vdd bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X110 a_918_6928# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X111 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X112 vss vss bg_pnp_c_0.e2 pnpMPA a=4p p=8u
X113 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X114 a_1575_6072# a_2119_3998# vss rhigh l=9.94u w=0.5u
X115 a_1847_6072# a_1439_3998# vss rhigh l=9.94u w=0.5u
X116 bg_n4_0.g bg_n4_0.g bg_n4_0.g vss sg13_hv_nmos ad=0.68p pd=4.68u as=0 ps=0 w=2u l=4u
X117 a_918_6928# bg_n4_0.vpc iout vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X118 vdd bg_n4_0.vpc vdd vdd sg13_hv_pmos ad=0.102p pd=1.28u as=0 ps=0 w=0.3u l=1u
X119 vdd bg_pmir_pcas_c_0.vpg a_918_8440# vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X120 a_3343_6072# a_3071_3998# vss rhigh l=9.94u w=0.5u
X121 a_918_6928# bg_pmir_pcas_c_0.vpg vdd vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
X122 bg_n4_0.vpc bg_n4_0.vpc bg_pmir_pcas_c_0.vpg vdd sg13_hv_pmos ad=3.4p pd=20.68u as=3.4p ps=20.68u w=10u l=1u
.ends

