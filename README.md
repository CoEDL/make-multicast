This script builds an Elan file using tiers from two input files.

File 1 includes a phrase transcription and free translation of a text.
File 2 includes the free translation that has been exported to FLEx, interlinearized, and then imported back into ELAN.
File 3 is the result. 

OMG.... probably would have been simpler to do this by parsing the XML. 
The complexities of this script are due to the hierarchies in the input files. 
Anyway, it was an interesting exercise in using pympi-ling. 

Requires patched version of Pympi-ling to get top-tier in a hierarchy of ref tiers when doing add_ref_annotation.
pip install git+https://github.com/dopefishh/pympi.git@57518a0fb646037c09f925ca3aa08b29cd20725a
BTW, This script won't run in PyCharm due to this custom pip install. Gotta do it in Terminal.