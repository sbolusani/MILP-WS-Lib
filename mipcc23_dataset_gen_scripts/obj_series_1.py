#!/usr/bin/python3

import sys, getopt, re, random, copy

def main(argv):
   corefile = ""
   metaofscenfiles = ""
   outputfilebasename = ""
   numinsts = 0

   try:
      opts,args=getopt.getopt(argv,"hc:s:o:n:",["corefile=","metaofscenfiles=","outputfilebasename=","numinsts="])
   except getopt.GetoptError:
      print("parse_smkp_v2.py -c <corefile> -s <metaofscenfiles> -o <outputfilebasename> -n <numinsts>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_smkp_v2.py -c <corefile> -s <metaofscenfiles> -o <outputfilebasename> -n <numinsts>")
         sys.exit()
      elif opt in ("-c", "--corefile"):
         corefile = arg
      elif opt in ("-s", "--metaofscenfiles"):
         metaofscenfiles = arg
      elif opt in ("-o", "--outputfilebasename"):
         outputfilebasename = arg
      elif opt in ("-n", "--numinsts"):
         if int(arg) > 0:
            numinsts = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   scenfilelist = []
   if metaofscenfiles == "":
      scenfilelist.append(corefile.split(".")[0]+".sto")
   else:
      with open(metaofscenfiles) as sfm:
         for line in sfm:
            scenfilelist.append(re.sub("\n", "", line))

   print("Core file: ", corefile)
   print("Scenario files: ", scenfilelist)

   if outputfilebasename == "":
      outputfilebasename = "smkp"

   cflines = []
   cols = 0
   objvec = {}
   with open(corefile) as cf:
      for line in cf:
         cflines.append(line)
         if line.split()[0] == "COLUMNS":
            cols = 1
         elif line.split()[0] == "RHS":
            cols = 0
         elif cols == 1:
            splitline = line.split()
            if splitline[0] in ["M0000001", "M0000002"]:
               continue
            else:
               if "obj" in splitline:
                  objindex = splitline.index("obj")
                  objvec[splitline[0]] = splitline[objindex + 1]
               else:
                  if splitline[0] not in objvec.keys():
                     objvec[splitline[0]] = 0

   numscen = 0
   scendata = []
   for scenfile in scenfilelist:
      with open(scenfile) as sf:
         for line in sf:
            if line.split()[0] in ["STOCH", "SCENARIOS", "ENDATA"]:
               continue
            elif line.split()[0] == "SC":
               numscen += 1
               scendata.append({})
            else:
               sfline = line.split()
               scendata[numscen-1][sfline[0]+"_"+sfline[1]] = sfline[2]

   startscen = 0
   scens2create = random.sample(range(numscen), numinsts)
   for filenum in range(numinsts):
      newnum = startscen + filenum + 1
      outputfile = outputfilebasename+"_"+str(newnum)+".mps"
      print("Writing output file: ", outputfile)
      scennum = scens2create[filenum]
      rows = 0
      cols = 0
      rhs = 0
      bounds = 0
      objveccopy = copy.deepcopy(objvec)
      with open(outputfile, "w") as of:
         for line in cflines:
            if line.split()[0] == "*":
               continue
            elif line.split()[0] == "NAME":
               of.write("NAME        "+outputfile.split(".")[0]+"\n")
            elif line.split()[0] == "ROWS":
               rows = 1
               cols = 0
               rhs = 0
               bounds = 0
               of.write(re.sub("\n", "", line)+"\n")
            elif line.split()[0] == "COLUMNS":
               rows = 0
               cols = 1
               rhs = 0
               bounds = 0
               of.write(re.sub("\n", "", line)+"\n")
            elif line.split()[0] == "RHS":
               rows = 0
               cols = 0
               rhs = 1
               bounds = 0
               of.write(re.sub("\n", "", line)+"\n")
            elif line.split()[0] == "BOUNDS":
               rows = 0
               cols = 0
               rhs = 0
               bounds = 1
               of.write(re.sub("\n", "", line)+"\n")
            elif line.split()[0] == "ENDATA":
               rows = 0
               cols = 0
               rhs = 0
               bounds = 0
               of.write(re.sub("\n", "", line)+"\n")
            elif rows == 1 or rhs == 1 or bounds == 1:
               of.write(re.sub("\n", "", line)+"\n")
            elif cols == 1:
               splitline = line.split()
               if "obj" in splitline:
                  if splitline[0]+"_obj" in scendata[scennum].keys():
                     numwhitespaces = [len(i) for i in re.findall('\s+',
                        re.sub("\n", "", line))]
                     objindex = splitline.index("obj")
                     if len(splitline[objindex + 1]) > len(scendata[scennum][splitline[0]+"_obj"]):
                        numwhitespaces[objindex+1] += len(splitline[objindex + 1]) - len(scendata[scennum][splitline[0]+"_obj"])
                     elif len(splitline[objindex + 1]) < len(scendata[scennum][splitline[0]+"_obj"]):
                        numwhitespaces[objindex+1] -= len(scendata[scennum][splitline[0]+"_obj"]) - len(splitline[objindex + 1])
                     splitline[objindex + 1] = scendata[scennum][splitline[0]+"_obj"]
                     objveccopy[splitline[0]] = scendata[scennum][splitline[0]+"_obj"]
                     newline = ""
                     for ind in range(len(splitline)):
                        newline += " "*numwhitespaces[ind]
                        newline += splitline[ind]
                     of.write(newline+"\n")
                  else:
                     of.write(re.sub("\n", "", line)+"\n")
               else:
                  of.write(re.sub("\n", "", line)+"\n")
            else:
               print("ALERT: Unknown line in core file!!")
               sys.exit()
      objvecfile = outputfilebasename+"_"+str(newnum)+"_obj"+".txt"
      print("Writing objective vector file: ", objvecfile)
      with open(objvecfile, "w") as ovf:
         for key in objveccopy.keys():
            ovf.write(objveccopy[key]+"\n")

if __name__ == "__main__":
   main(sys.argv[1:])
