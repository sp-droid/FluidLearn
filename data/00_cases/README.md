This should not be handled, for now, by the framework. This is just for the user to manually execute openFOAM and save the raw files by himself, it's not part of the library per se, and as long as the data has the same format it can be run through other software.



Version: openfoam2512

- Init WSL or a Linux distribution
- su [user, i.e. openFOAM]. Then introduce password
- conda activate [env, i.e. globalWSL]
- cd folder
- ./sim.sh