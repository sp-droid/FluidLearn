#!/bin/bash
startTotal=$(date +%s)

rm -rf ~/output
mkdir ~/output
echo "Writing dataset to ~/output..."
for ((i=0; i<36; i++)); do
    echo "🧹 Cleaning previous simulation directories..."
	foamListTimes -rm
	rm -rf ./VTK ./logs
	mkdir logs
	
	# This script changes the viscosity to get a different Re, and saves the json with the case constant parameters
	python preProcessing.py ${i} 36

	echo "🧩 Decomposing domain..."
	decomposePar > logs/decomposePar.log

	start=$(date +%s)

	echo "🛠️ Running parallel simulation with pimpleFoam..."
	mpirun -np 6 pimpleFoam -parallel > logs/foam.log

	end=$(date +%s)
	runtimeS=$((end - start))
	runtimeM=$((runtimeS / 60))
	runtimeS=$((runtimeS % 60))

	echo "📊 Extracting residuals with foamLog..."
	foamLog logs/foam.log > /dev/null

	echo "📈 Generating plots..."
	./plot.sh

	echo "🔗 Reconstructing domain"
	reconstructPar > logs/reconstructPar.log

	echo "🧹 Cleaning up processor directories..."
	rm -rf ./processor*

	endTotal=$(date +%s)
	totalRuntimeS=$((endTotal - startTotal))
	totalRuntimeM=$((totalRuntimeS / 60))
	totalRuntimeS=$((totalRuntimeS % 60))
	echo "✅ Simulation complete in ${runtimeM}m ${runtimeS}s (total: ${totalRuntimeM}m ${totalRuntimeS}s)"
	
	foamToVTK > /dev/null
	python postProcessing.py ${i}

	# # Open paraview file
	# explorer.exe para.foam
done

# cp -r ~/output /mnt/c/Users/a1pab/Desktop/TRANSDIFFUSE/Transdiffuse_ML/Pablo/02autoregressiveML2D/input/cylinder2D_8k/