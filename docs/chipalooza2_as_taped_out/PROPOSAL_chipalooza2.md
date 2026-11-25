<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Chipalooza #2 proposal (as submitted, 10 August 2026)

The proposal for slot 7 as submitted, reproduced unchanged below the line. Source: design repository
[`sudelbuecher/description/s2d_d2s_pinbuffers.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/30da354aab5fabb2059f0a1ce504bef34cb11246/sudelbuecher/description/s2d_d2s_pinbuffers.md)
on branch `sudel_buecher` (last changed in commit `6600fc1`, 2026-09-04; PDF:
[`s2d_d2s_pinbuffers.pdf`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/30da354aab5fabb2059f0a1ce504bef34cb11246/sudelbuecher/description/s2d_d2s_pinbuffers.pdf)).
What was taped out differs from it: see [README.md](README.md) and [ACHIEVED_VS_LIMITS.md](ACHIEVED_VS_LIMITS.md).

---

## Proposal for IP block development for the opencircuitdesign 2026 Chipalooza challenge

### IP Block name:

# Single ended to differential and differential to single ended analog pin buffers

### Designer/Design Team:

*Christoph Maier*

Email address: [*christoph.maier@ieee.org*](mailto:christoph.maier@ieee.org)

10 August 2026

## Circuit description

On-chip analog design building blocks (amplifiers, filters, comparators, ...) 
should be fully differential in/differential out, for signal range and PSRR.  

Multi-user shared design platform ASICs like Chipalooza, TinyTapeout, HeiChips, etc.  
are severely I/O limited.  

To alleviate the scarcity of I/O pins while facilitating fully differential designs in slots assigned to users, 
some building blocks are useful:  
  
* differential-in to single-ended out class AB analog pin driver  
* single-ended analog pin to fully differential internal signal buffer amplifier  
  
Generally, I'm more interested in all sorts of building blocks useful for an on-chip potbox [[http://opencircuitdesign.com/~tim/research/potbox/potbox.ps](http://opencircuitdesign.com/~tim/research/potbox/potbox.ps)] 
than a self-contained circuit presentable as a student project.  

To still allow a self-contained, demonstrable proof-of-concept slot, I intend to add  
  
* an internal common mode voltage reference to provide a sufficiently stable V<sub>CM</sub> for internal common mode feedback circuits  
* a proof-of-concept fully differential circuit (e.g., a g<sub>m</sub>C quadrature oscillator with differential input)  
* (if necessary) a buffered power supply for input and output pin buffers for PSRR  

## Circuit pinout

### from infrastructure
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| vdd3v3    | analog power               | 3.3V nominal                              |
| vdd1v2    | digital power              | 1.2V nominal                              |
| vss3v3    | analog ground              | 0V                                        |
| vss1v2    | digital ground             | 0V                                        |
| vssio     | I/O ground                 | 0V                                        |
| ibias     | bias current               | to be discussed, 100nA ballpark           |
| igmc      | g<sub>m</sub>C control current | to be discussed            |
| vbias     | common mode voltage        | to be discussed, if adjustable            |

### dedicated analog pins (maybe pins with integrated buffer circuits)
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| vin       | single ended analog in     | must include vssio, should include vdd3v3 |
| vout      | single ended analog out    |                                           |

### shared analog pins
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| vcm       | common mode voltage        | maybe switchable to internal V<sub>CM</sub> |
| vdiffp    | differential analog I/O    | "internal" differential voltage (buffered?) |
| vdiffn    | differential analog I/O    | "internal" differential voltage (buffered?) |


### shared digital input pins
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| ena       | master enable              |                                           |
| reset     | reset digital logic        | reset scan chain (and other logic?)       |
| outbuf_en | output pin buffer enable   |                                           |
| inbuf_en  | input pin buffer enable    | input of next internal stage to V<sub>CM</sub> if off |
| filter_en | internal g<sub>m</sub>C filter enable | inbuf connected to outbuf if disabled      |
| vdiff_en[1:0] | differential analog I/O enable | off, in, out, out_offset          |
|vcmsel[1:0]| V<sub>CM</sub> select      | analog pin, internal, infrastructure      |
| scanclk   | scan chain shift clock     |                                           |
| scanctrl[1:0] | scan chain control     | idle, shift, write, readback              |
| scanin    | scan chain in              |                                           |

### shared digital output pins
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| scanout   | scan chain out             |                                           |

*Note any changes from the specification, such as if trim bits have been
added.*

## Circuit architecture

* differential input class AB pin driver (integrated in pin?)  
* single ended input pin to differential signal input buffer (unity+negative unity gain, integrated in pin?)  
* switch logic to select common mode voltage (infrastructure, shared analog pin, or internal circuit)  
* switch logic to select bias current (infrastructure or internal, see [https://github.com/tatzelbrumm/ihp-sg13cmos5l-librelane-template/tree/tatzelbranch/xschem](https://github.com/tatzelbrumm/ihp-sg13cmos5l-librelane-template/tree/tatzelbranch/xschem))  
* fully differential g<sub>m</sub>C filter, control current provided by infrastructure or a variant of [the current DAC taped out to HeiChips](https://github.com/tatzelbrumm/PUDDING/blob/main/macro/gds/heichips25_pudding.gds)
* a [digital scan chain comprising a shift register and holding registers](https://github.com/tatzelbrumm/PUDDING/blob/tatzelbranch/src/heichips25_pudding.sv) for digital control as necessary

### External resources (if any) (all resources must be open source)

*List any resources that come from on chip, such as a bandgap-referenced
voltage or PTAT current, or from other IP blocks (such as a comparator
used in an ADC). List any external resources needed for testbench
circuits, including any digital control sequencing needed.*  
  
If possible, I will derive the pmos and nmos bias currents from layout structures that match the layout of the current and voltage references on the Chipalooza harness.  
Maybe I will cheat and design yet another of my favorite [Oguey&Aebischer bias](https://github.com/tatzelbrumm/ihp-sg13cmos5l-librelane-template/blob/tatzelbranch/xschem/OgueyAebischerBias.sch) blocks  
[[https://www.semanticscholar.org/paper/Ultra-High-Input-Impedance%2C-Low-Noise-Integrated-Chi-Maier/ab83669efb5f29a94e19b8e2c3f4801ab50ba3ea/figure/10](https://www.semanticscholar.org/paper/Ultra-High-Input-Impedance%2C-Low-Noise-Integrated-Chi-Maier/ab83669efb5f29a94e19b8e2c3f4801ab50ba3ea/figure/10)],    
[[https://github.com/MastellaM/sky130_TAC3/pull/3](https://github.com/MastellaM/sky130_TAC3/pull/3)]   
**with matching layout primitives**.  

### Specification difficulties

*List all specifications which may be difficult to attain, and what
circuit design methods will be used to meet those specifications. Note
where specifications will be affected by layout considerations, such as
mismatch, crosstalk, and I-R drop.*  
  
Bias currents, bandwidth, SNR and PSRR, Class AB output current and load capacitance are to be determined from what other participants in Chipalooza may find useful **(to be discussed)**.  
By default, I'd aim for low noise, low (10&hellip;100nA branch) current for internal amplifiers and some 10mA class AB output current into 100pF.  
  
Unless advised otherwise, I would aim for low (<1 MHz) bandwidth. If the input and output pin buffers become more useful to others, I'll aim for higher bandwidth.  
  
#### Claude tells me:  
  
Calibration tiers, output buffer (differential in → single-ended pin):

|              | GBW	| FPBW @1 V_pk | Risk |
|:-------------|:-----:|:------------:|:----:|
| Conservative | 1–5 MHz | ~1–2 MHz	| first silicon works, no drama |
| Reasonable   | 10–30 MHz | 5–10 MHz | the sweet spot; poles comfortably clear |
| Aggressive   | 50–100 MHz| 20 MHz	| pole management is now the whole design; MOScap C_c uncertainty becomes acute |
| Don't	       | >200 MHz | —stop calling it a buffer |

### Testbenches required for verifying circuit performance

*List what testbenches are used for each of the electrical parameters to
be tested, and briefly describe the testbench circuit setup and how it
measures the specified parameter.*  
  
For an unaffiliated individual, testbenches can be build from USB instruments that provide analog and digital pattern generation and logic analyzer/oscilloscope functionality.  
For unbuffered analog signals, an expensive active differential oscilloscope probe or a PCB with a high input impedance instrumentation amplifier will help.  
  
As proof of concept, a single ended input is fed through the input single ended to differential buffer, through the fully differential transconductance stages and through the output Class AB buffer.  

The g<sub>m</sub>C stages need to be configurable to operate both as a filter of the input signal and as quadrature oscillator that does not require input.  

It must be possible to disconnect the input buffer from the internal stages, by connecting the inputs to V<sub>CM</sub> instead.  

Two of the shared analog pins are used to feed fully differential signals to and from the internal stages.    
This will allow separate testing of the input and output buffer stages.    
Measuring unbuffered differential analog signals may require an external instumentation amplifier or, if feasible, 
auxiliary class AB amplifiers on chip driving the shared analog lines.  
  
#### Tests:  

1. input buffer off, output buffer on, filter off, differential input enabled (output buffer standalone)  
2. input buffer off, output buffer on, filter off (output buffer offset and noise)  
3. input buffer on, filter off, output buffer off, differential output enabled (input buffer standalone, measure V<sub>CM</sub>)  
4. input and output buffers on, filter off (output connects to input)  
5. input and output buffers on, filter on, filter configured as g<sub>m<\sub>C filter  
6. input buffer off, filter and output buffer on, filter configured as g<sub>m<\sub>C oscillator  
7. input buffer on, filter and output buffer on, filter configured as driven g<sub>m<\sub>C oscillator  
8. input and output buffers off, filter off, differential output shorted (shared analog pin and wire parasitics)  
9. input buffer and filter on, output buffer off, differential output enabled (characterize filter, measure V<sub>CM</sub>)  

### Connections required for standalone (breakout) implementation

*Indicate how the circuit is to be connected for individual testing
outside of the eventual SoC application, and where test points may need
to be added to access internal states of the circuit. Note where pad
capacitance, wirebond inductance, and wire resistance from pad to
circuit may affect measurement, and how to mitigate. Note where the
circuit may need to be placed as close as possible to a pad.*  

The following pins would have to be made available:

### from infrastructure moved to dedicated pins
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| vdd3v3    | analog power               | 3.3V nominal                              |
| vdd1v2    | digital power              | 1.2V nominal                              |
| vss3v3    | analog ground              | 0V                                        |
| vss1v2    | digital ground             | 0V                                        |
| vssio     | I/O ground                 | 0V                                        |
| ibias     | bias current               | to be discussed, 100nA ballpark           |
| igmc      | g<sub>m</sub>C control current | to be discussed            |
| vbias     | common mode voltage        | to be discussed, if adjustable            |

### analog pins, close to pad (and instrumentation amplifier close to the pad on the PCB side)
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| vcm       | common mode voltage        | maybe switchable to internal V<sub>CM</sub> |
| vdiffp    | differential analog I/O    | "internal" differential voltage (buffered?) |
| vdiffn    | differential analog I/O    | "internal" differential voltage (buffered?) |

### digital input pins (some dedicated input pins could be absorbed into the scan chain)
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| ena       | master enable              |                                           |
| reset     | reset digital logic        | reset scan chain (and other logic?)       |
| outbuf_en | output pin buffer enable   |                                           |
| inbuf_en  | input pin buffer enable    | input of next internal stage to V<sub>CM</sub> if off |
| filter_en | internal g<sub>m</sub>C filter enable | inbuf connected to outbuf if disabled      |
| vdiff_en[1:0] | differential analog I/O enable | off, in, out, out_offset          |
|vcmsel[1:0]| V<sub>CM</sub> select      | analog pin, internal, infrastructure      |
| scanclk   | scan chain shift clock     |                                           |
| scanctrl[1:0] | scan chain control     | idle, shift, write, readback              |
| scanin    | scan chain in              |                                           |

### digital output pins
| Pin name  | Use                        | Value                                     |
|:---------:|:--------------------------:|------------------------------------------:|
| scanout   | scan chain out             |                                           |



### Test plan for standalone (breakout) implementation

*Describe how the standalone circuit can be measured on a lab bench to
verify that the circuit meets performance requirements for each
specified electrical parameter.*  

* Serial data generator for digital control,  
* instrumentation amplifiers for unbuffered internal differential analog signals
* Provide the possibility to (capacitively? By transformer??) inject AC into the power lines and the analog I/O lines
to characterize PSRR, output resistance and such.  
  
