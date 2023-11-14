#!/usr/bin/python3

# The rotateObj method is copied from Jakob's script 'jakob_random_obj/randomObjective.py' and edited for our needs.

import sys, getopt, re, random, numpy as np, math
from copy import copy

def rotateObj(origdenseobjcoefs, numinstsperprob):
    # define a small offset to rotate axis where both variables has a zero coefficient in the objective
    offset = 1e-4;

    # generate set of all indices
    indexset = [i for i in range(len(origdenseobjcoefs))]

    # permute the indexset
    random.shuffle(indexset)

    # number of axis to rotate
    naxis = int(math.floor(len(indexset)/2))
    axis = 0

    # list of objs
    randobjs = []

    # init list of alphas
    alpha = [0]*naxis

    number_full_rotated = 0;
    addedaxis = 0

    # calc similarities
#    sim = [ round(i/numinstsperprob, 4) for i in range(numinstsperprob+1)]
#    sim = np.round(np.random.uniform(0.1, 0.6, size=numinstsperprob), 4)
#    sim = np.sort(sim).tolist()
#    sim.append(1.0)
#    sim[0] = 0.0
    sim = [round(i/numinstsperprob, 4) for i in range(numinstsperprob + 1)]

    # counter for current obj to be generated
    curobj = numinstsperprob-1

    # tmp obj
    tmp_obj = copy(origdenseobjcoefs)

    # ensure that i < j for all i-j-axis
    for i in range(naxis):
        if indexset[2*i] > indexset[2*i+1]:
            print("       Swapping indices!!")
            tmp = indexset[2*i]
            indexset[2*i] = indexset[2*i+1]
            indexset[2*i+1] = tmp
            assert indexset[2*i] < indexset[2*i+1]

    objfinish = False
    rotatezeros = False

    norm = np.linalg.norm(origdenseobjcoefs)
    norm *= norm

    while curobj >= 0 :
        print("Rotating obj ", curobj, " with sim ", sim[curobj])
        while objfinish == False:
            if alpha[axis] != 180:
                tmp_alpha = 0
                rad = 0
                deg = 0
                sum = 0

                for i in indexset:
                    if i != indexset[2*axis] and i != indexset[2*axis+1]:
                        sum += (origdenseobjcoefs[i]*tmp_obj[i])

                old_coef_0 = tmp_obj[indexset[2*axis]]
                old_coef_1 = tmp_obj[indexset[2*axis+1]]

                # skip zeros
#                if rotatezeros == False and (old_coef_0 == 0 or old_coef_1 == 0):
#                    continue

                if old_coef_0 == 0:
                    sgn = random.choice([-1,+1])
                    old_coef_0 = sgn * offset;

                if old_coef_1 == 0:
                    sgn = random.choice([-1,+1])
                    old_coef_1 = sgn * offset

                cos_of_alpha = (sim[curobj]*norm - sum)/(math.pow(old_coef_0,2) + math.pow(old_coef_1,2))

                if -1 <= cos_of_alpha and cos_of_alpha <= 1:
                    # get exact radians
                    tmp_alpha = math.acos(cos_of_alpha)

                    # calculate next integer degree
                    deg = round(math.degrees(tmp_alpha)) - alpha[axis] # additivity
                    # retransform into radients
                    rad = tmp_alpha - math.radians(alpha[axis])

                    # save degree
                    alpha[axis] = round(math.degrees(tmp_alpha))
                    objfinish = True
                else:
                    if alpha[axis] == 0:
                        tmp_alpha = random.randint(0,359)
                        alpha[axis] += tmp_alpha

                        # degree in radiant
                        rad = math.radians(tmp_alpha)
                    else:
                        if alpha[axis] < 180:
                            tmp_alpha = random.randint(0, 180 - alpha[axis])
                            alpha[axis] += tmp_alpha

                            # degree in radiant
                            rad = math.radians(tmp_alpha)
                        else:
                            tmp_alpha = random.randint(0, alpha[axis] - 180)
                            alpha[axis] -= tmp_alpha

                            # degree in radiant
                            rad = math.radians(-tmp_alpha)

                # rotate
                print("   About to rotate!")
                tmp_obj[indexset[2*axis]] = old_coef_0*math.cos(rad) + old_coef_1*math.sin(rad)
                tmp_obj[indexset[2*axis+1]] = old_coef_1*math.cos(rad) - old_coef_0*math.sin(rad)

                if alpha[axis] == 180:
                    number_full_rotated += 1

                if number_full_rotated == naxis:
                    alpha.append(0)
                    addedaxis += 1
                    naxis = min( naxis+1, math.floor(len(indexset)/2) )

            # go to the next axis
            print("    Going to next axis")
            axis = (axis + 1)%naxis

        if number_full_rotated == naxis:
            print("All " + str(naxis) + " axis are rotated by 180 degree. Reached sim " + str(calcSim(origdenseobjcoefs, tmp_obj)))

        randobjs.append(copy(tmp_obj))
        objfinish = False
        curobj -= 1

    return randobjs


def main(argv):
   metaofprobfiles = ""
   numinstsperprob = 0
   numcols = 0

   try:
      opts,args=getopt.getopt(argv,"hp:i:",["metaofprobfiles=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_multiobj.py -p <metaofprobfiles> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_multiobj.py -p <metaofprobfiles> -i <numinstsperprob>")
         sys.exit()
      elif opt in ("-p", "--metaofprobfiles"):
         metaofprobfiles = arg
      elif opt in ("-i", "--numinstsperprob"):
         if int(arg) > 0:
            numinstsperprob = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   objdict = {}
   probfiles = []
   allnumcols = {}
   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0] #re.sub("\n", "", line)
         probfiles.append(probfile)
         probfilebasename = probfile.split("/")[-1][:-4]
         allnumcols[probfilebasename] = int(splitline[1])
         numcols = allnumcols[probfilebasename]
         with open(probfile) as pf:
            obj = 0
            for pline in pf:
               splitline = pline.split()
               if splitline[0] in ["*", "OBJSENSE", "MIN", "RANGES"]:
                  continue
               elif splitline[0] == "NAME":
                  objdict[probfilebasename] = np.zeros(numcols)
                  continue
               elif splitline[0] == "COLUMNS":
                  obj = 1
                  continue
               elif splitline[0] == "RHS":
                  break

               if obj == 1:
                  if splitline[1]  == "Obj":
                     objdict[probfilebasename][int(splitline[0][1:])] = float(splitline[2])
                  if len(splitline) > 3 and splitline[3] == "Obj":
                     objdict[probfilebasename][int(splitline[0][1:])] = float(splitline[4])

   for probfile in probfiles:
      probfilebasename = probfile.split("/")[-1][:-4]
      numcols = allnumcols[probfilebasename]
      absmax = np.amax(np.absolute(objdict[probfilebasename]))
      absobj = np.absolute(objdict[probfilebasename])
      print("Building new objs for ", probfilebasename)
      newobjs = rotateObj(objdict[probfilebasename], numinstsperprob)
      filenumoffset = 150
      for i in range(numinstsperprob):
#         newobj1 = np.round(np.random.uniform(-absmax, absmax, numcols), 2)
#         newobj1 = [np.round(np.random.uniform(-absobj[i], absobj[i], 1), 2) for i in range(numcols)]
#         percentvariation = np.round(np.random.uniform(-9, 722, numcols), 2)
#         newobj1 = np.round(objdict[probfilebasename] + np.multiply(objdict[probfilebasename], percentvariation)/100, 2)
         newobj1 = np.round(newobjs[i], 15).tolist()
         assert(len(newobj1) == numcols)
         outdatfile = probfilebasename+"_"+str(i + filenumoffset)+"_obj.txt"

         print("Writing dat file ", outdatfile)
         with open(outdatfile, "w") as odf:
            for j in range(numcols):
               if objdict[probfilebasename][j] == 0:
                  odf.write(str(0.00)+"\n")
               else:
                  odf.write(str(newobj1[j])+"\n")

         outfile1 = probfilebasename+"_"+str(i + filenumoffset)+".mps"
         print("Writing MPS file ", outfile1)
         rows = 0
         cols = 0
         rhs = 0
         bounds = 0
         with open(probfile) as pf, open(outfile1, "w") as of1:
            obj = 0
            for line in pf:
               if line.split()[0] in ["*", "OBJSENSE", "MIN", "RANGES"]:
                  continue
               elif line.split()[0] == "NAME":
                  of1.write("NAME        "+outfile1[:-4]+"\n")
               elif line.split()[0] == "ROWS":
                  rows = 1
                  cols = 0
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "COLUMNS":
                  rows = 0
                  cols = 1
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "RHS":
                  rows = 0
                  cols = 0
                  rhs = 1
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "BOUNDS":
                  rows = 0
                  cols = 0
                  rhs = 0
                  bounds = 1
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "ENDATA":
                  rows = 0
                  cols = 0
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif rows == 1 or rhs == 1 or bounds == 1:
                  of1.write(re.sub("\n", "", line)+"\n")
               elif cols == 1:
                  splitline = line.split()
                  splitline1 = line.split()
                  numwhitespaces1 = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                  index = -1
                  if splitline[1] == "Obj":
                     index = 1
                  elif len(splitline) == 5 and splitline[3] == "Obj":
                     index = 3
                  if index > 0:
                     colnum = int(splitline[0][1:])
                     if objdict[probfilebasename][colnum] != 0:
                        if len(splitline[index + 1]) > len(str(newobj1[colnum])):
                           numwhitespaces1[index+1] += len(splitline[index + 1]) - len(str(newobj1[colnum]))
                        elif len(splitline[index + 1]) < len(str(newobj1[colnum])):
                           numwhitespaces1[index+1] -= len(str(newobj1[colnum])) - len(splitline[index + 1])
                        splitline1[index + 1] = str(newobj1[colnum])
                  newline1 = ""
                  for ind in range(len(splitline)):
                     newline1 += " "*numwhitespaces1[ind]
                     newline1 += splitline1[ind]
                  of1.write(newline1+"\n")
               else:
                  print("ALERT: Unknown line in MPS file!!")
                  sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
