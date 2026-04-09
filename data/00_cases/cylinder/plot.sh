#!/bin/bash

gnuplot -persist > /dev/null << EOF
	set terminal pngcairo size 1920, 1080 enhanced font "Verdana-Bold,16"
	set output "logs/Residuals.png"
	set logscale y
	set title "Simulation residuals"
	set xlabel "Time [s]"
	set ylabel "Residual"
	set grid
	
	plot "logs/pFinalRes_0" with lines lw 2 title "p - Pressure",\
		"logs/UxFinalRes_0" with lines lw 2 title "Ux - Vel. x",\
		"logs/UyFinalRes_0" with lines lw 2 title "Uy - Vel. y",\
		0.001 with lines lc rgb "red" lw 2 dt 2 title "Solver convergence threshold"
EOF

gnuplot -persist > /dev/null << EOF
	set terminal pngcairo size 1920, 1080 enhanced font "Verdana-Bold,16"
	set output "logs/Courant.png"
	set title "Simulation stability"
	set xlabel "Time [s]"
	set ylabel "Courant number"
	set y2label "Timestep size [ms]"
	set grid
	set ytics nomirror
	set y2tics
	set key bottom right

	
	plot "logs/CourantMax_0" using 1:2 with lines lw 2 title "Courant number",\
		1 with lines lc rgb "red" lw 2 dt 2 title "Courant–Friedrichs–Lewy threshold",\
		"logs/deltaT_0" using 1:( $ 2 * 1000) axes x1y2 with lines lw 2 title "Timestep size"
EOF