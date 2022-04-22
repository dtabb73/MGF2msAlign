# MGF2msAlign
# Created and translated from MATLAB
# by Kyowon Jeong, University of Tuebingen
# Initial version: April 21, 2022

import sys

n = len(sys.argv)
if n != 4:
    print('Usage: python mgf2msalign.py [input mgf file] [output msalign file] [activation (CID, ETD, or HCD)]')
    sys.exit()

mgf = sys.argv[1]
msalign = sys.argv[2]
act = sys.argv[3]

file1 = open(mgf, 'r')
file2 = open(msalign, 'w')

Lines = file1.readlines()

proton_mass = 1.007276466621


class Spec:
    id = 1

    def __init__(self,act):
        self.mz = .0
        self.intensity = .0
        self.scan = 0
        self.activation = act
        self.premz = .0
        self.preintensity = .0
        self.premass = .0
        self.precharge = 0
        self.rt = .0
        self.peaks = []

    def addPeaks(self, str):
        tstr = str.split('	')
        tpeaks = [float(tstr[0]), float(tstr[1]), int(tstr[2][0:-1])]
        self.peaks.append(tpeaks)

    def len(self):
        return len(self.peaks)

    def tomsalign(self):
        tstr = "BEGIN IONS\nID="
        tstr += str(Spec.id)
        tstr += "\nSCANS="
        tstr += str(self.scan)
        tstr += "\nACTIVATION="+self.activation
        tstr += "\nPRECURSOR_MZ="
        tstr += str(self.premz)
        tstr += "\nPRECURSOR_CHARGE="
        tstr += str(self.precharge)
        tstr += "\nPRECURSOR_MASS="
        tstr += str(self.precharge * (self.premz - proton_mass))
        tstr += "\nPRECURSOR_INTENSITY="
        tstr += str(self.preintensity)
        tstr += "\nRETENTION_TIME="
        tstr += str(self.rt) + "\n"
        for peak in self.peaks:
            tstr+=str(peak[0])+" "+str(peak[1])+" "+str(peak[2])+"\n"
        tstr += "END IONS\n"
        Spec.id += 1
        return tstr

spec = Spec(act)

# Strips the newline character
for line in Lines:
    if not line:
        break
    line = line.strip()
    if len(line) == 0:
        continue
    elif line.startswith("BEGIN IONS"):  # when a spec begins, reset all buffers
        spec = Spec(act)
    elif line.startswith("END IONS"):  # when a spec ends write to msalign
        if spec.len() > 0:
            file2.write(spec.tomsalign())
    elif line.startswith("SCANS"):
        spec.scan = int(line.split("=")[1])
    elif line.startswith("RTINSECONDS"):
        spec.rt = float(line.split("=")[1])
    elif line.startswith("CHARGE"):
        spec.precharge = int(line.split("=")[1][0:-1])
        if  spec.precharge == 0:
            spec.precharge = 1
    elif line.startswith("PEPMASS"):
        tstr = line.split("=")[1].split(' ')
        spec.premz = float(tstr[0])
        spec.preintensity = float(tstr[1])
    elif line[0].isdigit():
        spec.addPeaks(line)

file2.close()
file1.close()
