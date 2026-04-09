#!/bin/bash
startTotal=$(date +%s)


echo "🧹 Cleaning previous simulation directories..."
foamListTimes -rm
rm -rf ./VTK ./logs
mkdir logs

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

explorer.exe para.foam